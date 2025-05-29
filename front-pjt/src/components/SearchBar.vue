<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";

const searchQuery = ref("");
const router = useRouter();
const route = useRoute();

function onSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: "/news", query: { ...route.query, q: searchQuery.value } });
    searchQuery.value = "";
  }
}
</script>

<template>
  <form @submit.prevent="onSearch" class="search-bar">
    <input
      v-model="searchQuery"
      type="text"
      placeholder="검색어를 입력하세요"
      class="search-input"
    />
    <button type="submit" class="search-btn">검색</button>
  </form>
</template>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}
.search-input {
  padding: 8px 12px;
  border: 1px solid #ccc;
  background-color: #fff;
  border-radius: 4px;
  flex-grow: 1;
}
.search-btn {
  padding: 7px 20px;
  background: #272c97;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>