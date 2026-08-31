/**
 * 令牌存储：内存 + localStorage 持久化，作为 axios 拦截器与 SSE 换票的令牌来源。
 */
const ACCESS_KEY = "autocustomer.access_token";
const REFRESH_KEY = "autocustomer.refresh_token";

export interface TokenStore {
  getAccessToken(): string | null;
  getRefreshToken(): string | null;
  setTokens(access: string, refresh?: string): void;
  clear(): void;
}

function read(key: string): string | null {
  if (typeof localStorage === "undefined") return null;
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string): void {
  if (typeof localStorage === "undefined") return;
  try {
    localStorage.setItem(key, value);
  } catch {
    /* ignore */
  }
}

function remove(key: string): void {
  if (typeof localStorage === "undefined") return;
  try {
    localStorage.removeItem(key);
  } catch {
    /* ignore */
  }
}

export const tokenStore: TokenStore = {
  getAccessToken: () => read(ACCESS_KEY),
  getRefreshToken: () => read(REFRESH_KEY),
  setTokens(access, refresh) {
    write(ACCESS_KEY, access);
    if (refresh !== undefined) write(REFRESH_KEY, refresh);
  },
  clear() {
    remove(ACCESS_KEY);
    remove(REFRESH_KEY);
  },
};