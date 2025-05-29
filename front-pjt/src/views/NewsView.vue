<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import ContentBox from "@/common/ContentBox.vue";
import NewsCard from "@/components/NewsCard.vue";
import { tabs } from "@/assets/data/tabs";
import PaginationButton from "@/common/PaginationButton.vue";
import StateButton from "@/common/StateButton.vue";
import SearchBar from "@/components/SearchBar.vue";
import axios from 'axios'

const route = useRoute();
const router = useRouter();

const newsList = ref([]);
const sortBy = ref(route.query.sort || "latest");
const activeTab = ref(route.query.category || tabs[0].id);
const currentPage = ref(1);
const totalPages = ref(1);
const username = ref(localStorage.getItem("username"));

// URL 파라미터 업데이트 함수
const updateUrlParams = () => {
  const query = {
    sort: sortBy.value,
    category: activeTab.value === tabs[0].id ? undefined : activeTab.value
  };
  router.replace({ query: Object.fromEntries(Object.entries(query).filter(([_, v]) => v !== undefined)) });
};

// 뉴스 요청 함수
const fetchNews = async () => {
  if (route.query.q) {
    // 실제 검색 API 호출
    try {
      const res = await axios.get(`http://localhost:8000/api/news/search/`, {
        params: { q: route.query.q },
        headers: {
          Authorization: `Token ${localStorage.getItem("access")}`,
        },
      });
      newsList.value = res.data.results || [];
      console.log(`🔍 검색 결과: ${newsList.value.length}건`);
    } catch (err) {
      console.error("❌ 검색 실패:", err);
      newsList.value = [];
    }
  } else {
    try {
      let endpoint = "";
      const queryParams = new URLSearchParams();

      // 추천순 선택 시 추천 API 호출
      if (sortBy.value === "recommend") {
        endpoint = "http://localhost:8000/api/user/recommend/";
      } else {
        // 카테고리별 뉴스 요청
        const selectedTab = tabs.find((tab) => tab.id === activeTab.value);
        const category = selectedTab?.value || "";
        endpoint = category
          ? `http://localhost:8000/api/news/category/${encodeURIComponent(category)}/`
          : "http://localhost:8000/api/news/";
        
        // 정렬 파라미터 추가
        if (sortBy.value !== "latest") {
          queryParams.append("sort", sortBy.value);
        }
      }

      const res = await axios.get(`${endpoint}?${queryParams.toString()}`, {
        headers: {
          Authorization: `Token ${localStorage.getItem("access")}`,
        },
      });

      newsList.value = res.data;
      console.log(`🟢 [${sortBy.value}] 뉴스 ${res.data.length}건`);
    } catch (err) {
      console.error("❌ 뉴스 불러오기 실패:", err);
    }
  }
};

// 페이지 로드 시 뉴스 불러오기
onMounted(() => {
  // URL 파라미터가 있으면 그 값을 사용
  if (route.query.sort) {
    sortBy.value = route.query.sort;
  }
  if (route.query.category) {
    activeTab.value = route.query.category;
  }
  fetchNews();
});

// 드롭다운(정렬기준) 변경 시 뉴스 다시 불러오기
watch(sortBy, () => {
  updateUrlParams();
  fetchNews();
});

// 카테고리 변경 시 뉴스 다시 불러오기
watch(activeTab, () => {
  updateUrlParams();
  fetchNews();
});

// URL 파라미터 변경 감지
watch(() => route.query, (newQuery) => {
  if (newQuery.sort && newQuery.sort !== sortBy.value) {
    sortBy.value = newQuery.sort;
  }
  if (newQuery.category && newQuery.category !== activeTab.value) {
    activeTab.value = newQuery.category;
  }
  fetchNews();
}, { deep: true });

</script>

<template>
  <div class="news">
    <div>
      <h1 class="news__title">🤖 AI 맞춤 추천 뉴스</h1>
      <p class="news__description">
        당신이 원하는 뉴스, 이제 AI가 직접 추천해드립니다!<br />
        나만의 취향을 기반으로, 맞춤형 뉴스만 쏙쏙 골라주는<br />
        뉴스 큐레이팅 서비스
        <strong style="font-weight: bold">SSAFYNEWS</strong>에 빠져보세요.
        <br />AI 챗봇과 기사에 대해 대화하며 궁금한 점을 물어보고, <br />한눈에
        보기 쉬운 대시보드를 통해 나의 뉴스 소비 패턴도 확인할 수 있습니다.
      </p>

      <ContentBox class="news__tabs">
        <StateButton
          v-for="tab in tabs"
          :key="tab.id"
          type="state"
          :is-active="activeTab === tab.id"
          @click="() => { activeTab = tab.id; fetchNews(); }"
          >
          {{ tab.label }}
        </StateButton>
      </ContentBox>
    </div>
    <SearchBar />
    <ContentBox class="news__box">
      <div class="news__box__title-container">
        <div class="filters__container">
          <select class="filters" v-model="sortBy">
            <option value="latest">최신순</option>
            <option value="recommend">추천순</option>
          </select>
        </div>
      </div>
      <div v-if="username">
        <h1>📢 {{ username }} 님을 위한 뉴스 피드 </h1>
      </div>
      <div class="news__box__cards">
        <template v-for="news in newsList" :key="news?.id">
          <NewsCard v-if="news && news.title && news.writer" :data="news" />
        </template>
      </div>

      <PaginationButton v-model="currentPage" :totalPages="totalPages" />
    </ContentBox>
  </div>
</template>

<style scoped lang="scss">
.news__username {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 15px 0;
  color: #444;
}

.news {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;

  &__title {
    font-size: 20px;
    font-weight: 700;
    border-bottom: 1px solid #e2e2e2;
    padding-bottom: 10px;
  }

  &__description {
    font-size: 16px;
    font-weight: 400;
    color: #575757;
    line-height: normal;
    margin: 15px 0 25px;

    &--job {
      color: red;
      margin-bottom: 20px;
    }
  }

  &__tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px 30px !important;
  }

  &__box {
    padding: 30px !important;

    &__noti {
      color: #666666;
      font-size: 12px;
      padding: 5px 10px;
    }

    &__title-container {
      position: relative;
      display: flex;
      align-items: center;
    }

    &__title {
      font-weight: 700;
      font-size: 21px;
      cursor: pointer;

      &-username {
        font-weight: 400;
        padding: 3px;
        border-bottom: 2px solid #272c97;
      }
      &-icon {
        font-size: 15px;
      }
    }

    &__subtitle-loggedin {
      font-weight: 400;
      padding: 10px 0 0 10px;
      color: #575757;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
      text-decoration: underline;
    }

    &__title-container:hover .news__box__subtitle-loggedin {
      opacity: 1;
    }

    .filters__container {
      position: absolute;
      right: 0;
    }

    &__cards {
      margin-top: 30px;
      margin-left: 30px;
    }
  }
}
</style>
