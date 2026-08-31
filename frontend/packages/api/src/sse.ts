/**
 * SSE 流式对话封装。
 *
 * 鉴权约定（与 /design/01-architecture/frontend.md 对齐）：
 * 1. EventSource 无法携带 Authorization header，故先 POST /chat/stream-ticket（JWT header）换一次性 ticket；
 * 2. 再以 EventSource(`...?ticket=...`) 建流；
 * 3. 断线由 onerror 触发，重新换票 + 携带 last_event_id 参数重建（不依赖浏览器自动重连）。
 */

/** 服务端下发的流式帧：`data: {delta, done, msg_id}` */
export interface StreamFrame {
  delta: string;
  done: boolean;
  msg_id?: number;
}

export interface SseChatOptions {
  /** 建流端点，如 `${baseURL}/chat/sessions/1/stream` */
  url: string;
  /** 换票函数：返回一次性 ticket */
  fetchTicket: () => Promise<string>;
  /** 收到 delta 增量 */
  onDelta: (delta: string) => void;
  /** 流结束（done=true 或连接关闭） */
  onDone: (msgId?: number) => void;
  /** 出错（可恢复时触发重连，不可恢复时终止） */
  onError?: (err: unknown) => void;
  /** 最大自动重连次数，默认 3 */
  maxRetries?: number;
}

export class SseChatStream {
  private source: EventSource | null = null;
  private lastEventId = "";
  private retries = 0;
  private closed = false;
  private readonly opts: SseChatOptions;

  constructor(opts: SseChatOptions) {
    this.opts = opts;
  }

  async start(): Promise<void> {
    this.closed = false;
    await this.connect();
  }

  private async connect(): Promise<void> {
    if (this.closed) return;
    const ticket = await this.opts.fetchTicket();
    const sep = this.opts.url.includes("?") ? "&" : "?";
    const url = `${this.opts.url}${sep}ticket=${encodeURIComponent(ticket)}${
      this.lastEventId ? `&last_event_id=${encodeURIComponent(this.lastEventId)}` : ""
    }`;

    const source = new EventSource(url);
    this.source = source;

    source.onmessage = (ev: MessageEvent<string>) => {
      this.lastEventId = (ev as MessageEvent & { lastEventId?: string }).lastEventId ?? this.lastEventId;
      if (!ev.data) return;
      try {
        const frame = JSON.parse(ev.data) as StreamFrame;
        this.opts.onDelta(frame.delta);
        if (frame.done) {
          this.opts.onDone(frame.msg_id);
          this.close();
        }
      } catch {
        // 非 JSON 帧（如注释），忽略
      }
    };

    source.onerror = () => {
      source.close();
      if (this.closed) return;
      const max = this.opts.maxRetries ?? 3;
      if (this.retries >= max) {
        this.opts.onError?.(new Error("sse max retries exceeded"));
        this.close();
        return;
      }
      this.retries += 1;
      // 指数退避后重连
      setTimeout(() => void this.connect(), Math.min(1000 * 2 ** this.retries, 8000));
    };
  }

  close(): void {
    this.closed = true;
    this.source?.close();
    this.source = null;
  }
}