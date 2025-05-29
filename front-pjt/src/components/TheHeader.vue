<script setup>
import { RouterLink, useRouter } from "vue-router";
import { ref, watchEffect } from "vue";
import SearchBar from "@/components/SearchBar.vue";

const router = useRouter();

// 로그인 상태를 추적하는 반응형 변수
const isAuthenticated = ref(false);

watchEffect(() => {
  isAuthenticated.value = !!localStorage.getItem("access");
});

const refreshPage = (event) => {
  event.preventDefault();
  router.push("/").then(() => {
    window.location.reload();
  });
};

const logout = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  isAuthenticated.value = false;
  router.push("/login");
};
</script>

<template>
  <div class="header__container">
    <header>
      <router-link to="/" @click="refreshPage">
        <span class="logo"> SSAFYNEWS </span>
      </router-link>

      <nav class="menus">
        <div style="flex:1"></div>
        <!-- <SearchBar /> -->
        <router-link to="/news" @click="refreshPage">나만의 뉴스 큐레이팅</router-link>
        <router-link to="/dashboard">대시보드</router-link>
        <router-link v-if="!isAuthenticated" to="/login">로그인</router-link>
        <button v-else @click="logout" class="logout-btn">로그아웃</button>
      </nav>
    </header>
  </div>
</template>


<style scoped lang="scss">
.header__container {
  background-color: white;
  border-bottom: 1px solid #d4d4d4;
  header {
    max-width: 1280px;
    margin: 0 auto;
    color: black;
    height: 80px;
    justify-content: space-between;
    align-items: center;
    display: flex;
    padding: 0 15px;
  }

  .logo {
    font-size: x-large;
    font-weight: 800;
  }

  .menus {
    display: flex;
    align-items: center;
    gap: 23px;
  }

  a.router-link-active {
    font-weight: bold;
  }
}
</style>
