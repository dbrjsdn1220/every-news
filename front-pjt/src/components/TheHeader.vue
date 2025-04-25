<script setup>
import { RouterLink, useRouter } from "vue-router";

const router = useRouter();

const refreshPage = (event) => {
  event.preventDefault();
  router.push("/").then(() => {
    window.location.reload();
  });
};
</script>

<template>
  <div class="header__container">
    <header>
      <router-link to="/" @click="refreshPage">
        <span class="logo"> SSAFYNEWS </span>
      </router-link>

      <nav class="menus">
        <router-link to="/news">나만의 뉴스 큐레이팅</router-link>
        <router-link to="/dashboard">대시보드</router-link>
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
