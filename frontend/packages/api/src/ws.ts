/**
 * WebSocket 封装（坐席实时工单）：
 * - 心跳 30s
 * - 指数退避自动重连
 * - 消息信封 { type, seq, payload }
 */

export interface WsMessage<T = unknown> {
  type: string;
  seq: number;
  payload: T;
}

export interface WsClientOptions {
  url: string;
  heartbeatMs?: number;
  maxRetries?: number;
  onMessage: (msg: WsMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (err: Event) => void;
}

export class WsClient {
  private ws: WebSocket | null = null;
  private heartbeatTimer: number | null = null;
  private retries = 0;
  private closed = false;
  private seq = 0;
  private readonly opts: WsClientOptions;

  constructor(opts: WsClientOptions) {
    this.opts = opts;
  }

  connect(): void {
    if (this.closed) return;
    this.ws = new WebSocket(this.opts.url);

    this.ws.onopen = () => {
      this.retries = 0;
      this.opts.onOpen?.();
      this.startHeartbeat();
    };

    this.ws.onmessage = (ev: MessageEvent<string>) => {
      try {
        const msg = JSON.parse(ev.data) as WsMessage;
        this.opts.onMessage(msg);
      } catch {
        /* ignore */
      }
    };

    this.ws.onclose = () => {
      this.stopHeartbeat();
      this.opts.onClose?.();
      this.scheduleReconnect();
    };

    this.ws.onerror = (ev) => {
      this.opts.onError?.(ev);
    };
  }

  /** 发送带自增 seq 的消息 */
  send(type: string, payload: unknown): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.seq += 1;
    this.ws.send(JSON.stringify({ type, seq: this.seq, payload }));
  }

  close(): void {
    this.closed = true;
    this.stopHeartbeat();
    this.ws?.close();
    this.ws = null;
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    const interval = this.opts.heartbeatMs ?? 30_000;
    this.heartbeatTimer = window.setInterval(() => {
      this.send("ping", {});
    }, interval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer !== null) {
      window.clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.closed) return;
    const max = this.opts.maxRetries ?? 5;
    if (this.retries >= max) return;
    this.retries += 1;
    const delay = Math.min(1000 * 2 ** this.retries, 30_000);
    setTimeout(() => this.connect(), delay);
  }
}