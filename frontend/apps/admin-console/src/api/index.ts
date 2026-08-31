import { createApi, createApiClient, tokenStore } from "@auto/api";
import type { AutoApi } from "@auto/api";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const client = createApiClient({
  baseURL,
  onUnauthorized: () => {
    tokenStore.clear();
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("auth:unauthorized"));
    }
  },
});

export const api: AutoApi = createApi(client);

/** 登录并持久化令牌。 */
export async function login(username: string, password: string): Promise<void> {
  const resp = await client.post("/auth/login", { username, password });
  tokenStore.setTokens(resp.data.access_token, resp.data.refresh_token);
}