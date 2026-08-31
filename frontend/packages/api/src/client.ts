/**
 * axios 客户端封装：
 * - 注入 JWT（Authorization: Bearer）
 * - 401 静默刷新（单飞，避免并发刷新风暴）
 * - 统一错误归一化为 ApiError
 */
import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  InternalAxiosRequestConfig,
} from "axios";
import type { LoginRequest, TokenResponse } from "@auto/shared";
import { tokenStore } from "./token";

export interface ApiClientOptions {
  baseURL: string;
  /** 401 时回调（例如跳转登录页），可省略 */
  onUnauthorized?: () => void;
  /** 自定义 token 读取，默认使用 tokenStore */
  getAccessToken?: () => string | null;
}

let refreshPromise: Promise<string> | null = null;

export function createApiClient(options: ApiClientOptions): AxiosInstance {
  const getAccessToken = options.getAccessToken ?? (() => tokenStore.getAccessToken());

  const client: AxiosInstance = axios.create({
    baseURL: options.baseURL,
    timeout: 15_000,
    headers: { "Content-Type": "application/json" },
  });

  client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token) {
      config.headers.set("Authorization", `Bearer ${token}`);
    }
    return config;
  });

  client.interceptors.response.use(
    (resp) => resp,
    async (error: AxiosError) => {
      const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
      const status = error.response?.status;

      if (status === 401 && original && !original._retry) {
        original._retry = true;
        try {
          const token = await refreshAccessToken(client);
          original.headers.set("Authorization", `Bearer ${token}`);
          return client.request(original);
        } catch {
          tokenStore.clear();
          options.onUnauthorized?.();
          throw error;
        }
      }

      throw error;
    },
  );

  return client;
}

async function refreshAccessToken(client: AxiosInstance): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const refreshToken = tokenStore.getRefreshToken();
      if (!refreshToken) throw new Error("no refresh token");

      const resp = await axios.post<TokenResponse>(
        `${client.defaults.baseURL}/auth/refresh`,
        { refresh_token: refreshToken },
        { headers: { Authorization: `Bearer ${refreshToken}` } },
      );
      tokenStore.setTokens(resp.data.access_token, resp.data.refresh_token);
      return resp.data.access_token;
    })().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

export async function login(client: AxiosInstance, req: LoginRequest): Promise<TokenResponse> {
  const resp = await client.post<TokenResponse>("/auth/login", req);
  tokenStore.setTokens(resp.data.access_token, resp.data.refresh_token);
  return resp.data;
}

export { AxiosError };
export type { AxiosRequestConfig };