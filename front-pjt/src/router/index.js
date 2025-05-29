import NotFoundView from "@/views/NotFoundView.vue";
import { createRouter, createWebHistory } from "vue-router";
import NewsView from "@/views/NewsView.vue";
import NewsDetailView from "@/views/NewsDetailView.vue";
import DashBoardView from "@/views/DashBoardView.vue";
// import NewsView from "@/views/NewsView.vue";
console.log("NewsView 컴포넌트:", NewsView);

const router = createRouter({
  history: createWebHistory("/"),
  routes: [
    {
      path: "/",
      redirect: "/news",
    },
    {
      path: "/news",
      name: "News",
      component: NewsView,
    },
    {
      path: "/api/news/:id",
      name: "newsDetail",
      component: NewsDetailView,
      props: true,
      // meta: { requiresAuth: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashBoardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/:pathMatch(.*)*",
      component: NotFoundView,
    },
    {
      path: "/register",
      name: "RegisterView",
      component: () => import("@/views/RegisterView.vue"),
    },
    {
      path: "/login",
      name: "Login",
      component: () => import("@/views/LoginView.vue"),
    }
  ],
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const isAuthenticated = !!localStorage.getItem("access");

  if (requiresAuth && !isAuthenticated) {
    alert("로그인 후 사용할 수 있습니다.");
    next("/login");
  } else {
    next();
  }
});

export default router;
