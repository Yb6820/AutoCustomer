import type { Directive } from "vue";
import { useAuthStore } from "../stores/auth";

/**
 * 按钮级权限指令：v-perm="'kb:doc:publish'"
 * 无权限时直接移除元素（前端体验层，最终安全由后端 require_permission 兜底）。
 */
export const perm: Directive<HTMLElement, string> = {
  mounted(el, binding) {
    const auth = useAuthStore();
    const code = binding.value;
    if (code && !auth.hasPerm(code)) {
      el.parentNode?.removeChild(el);
    }
  },
};