import { createRouter, createWebHistory } from "vue-router";
import { tokenStore } from "@auto/api";
import AdminLayout from "../layouts/AdminLayout.vue";
import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";
import KbView from "../views/KbView.vue";
import TicketsView from "../views/TicketsView.vue";
import UsersView from "../views/UsersView.vue";
import RolesView from "../views/RolesView.vue";

export interface MenuItem {
  path: string;
  title: string;
}

/** 侧边栏静态菜单（后端 /auth/menus 就绪后改为动态生成） */
export const menuItems: MenuItem[] = [
  { path: "/dashboard", title: "数据概览" },
  { path: "/knowledge", title: "知识库" },
  { path: "/tickets", title: "工单管理" },
  { path: "/users", title: "用户管理" },
  { path: "/roles", title: "角色管理" },
];

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    {
      path: "/",
      component: AdminLayout,
      redirect: "/dashboard",
      children: [
        { path: "dashboard", name: "dashboard", component: DashboardView, meta: { title: "数据概览" } },
        { path: "knowledge", name: "knowledge", component: KbView, meta: { title: "知识库" } },
        { path: "tickets", name: "tickets", component: TicketsView, meta: { title: "工单管理" } },
        { path: "users", name: "users", component: UsersView, meta: { title: "用户管理" } },
        { path: "roles", name: "roles", component: RolesView, meta: { title: "角色管理" } },
      ],
    },
  ],
});

router.beforeEach((to) => {
  const authed = tokenStore.getAccessToken() !== null;
  if (!to.meta.public && !authed) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
  return true;
});