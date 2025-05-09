<script setup>
import { ref } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import router from "@/router";
import LeftArrow from "@/components/icon/LeftArrow.svg";
import ArticlePreview from "@/components/ArticlePreview.vue";
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "@/utils/axios";


const route = useRoute();
const news = ref();
const relatedNews = ref(null);

const { formatDate } = useDate();

const liked = ref(false);
const likeCount = ref(0);
const isAnimating = ref(false);

onMounted(async () => {
  const { id } = route.params;

  try {
    const res = await api.get(`http://localhost:8000/news/detail/${id}/`);
    news.value = res.data;
    likeCount.value = res.data.article_interaction?.likes || 0;
    liked.value = res.data.article_interaction?.liked ?? false;

    const relatedRes = await api.get(`http://localhost:8000/news/detail/${id}/related/`);
    relatedNews.value = relatedRes.data;
  } catch (err) {
    console.error("기사 상세 조회 실패:", err);
  }
});


const toggleLike = async () => {
  if (!localStorage.getItem("access") || !localStorage.getItem("user_id")) {
    alert("로그인 후 사용할 수 있습니다.");
    return;
  }

  const { id } = route.params;
  const user_id = localStorage.getItem("user_id");

  try {
    const formData = new FormData();
    formData.append("user_id", user_id);
    formData.append("article_id", id);

    const response = await api.post("http://localhost:8000/news/like/", formData, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access")}`,
      },
    });

    // 서버가 "Already liked"만 보내는 방식이라면 toggle이 안 되니
    if (response.data.message === "Like added") {
      liked.value = true;
      likeCount.value += 1;
    } else if (response.data.message === "Already liked") {
      alert("이미 좋아요를 누르셨습니다.");
    }

    isAnimating.value = true;
    setTimeout(() => (isAnimating.value = false), 600);
  } catch (err) {
    console.error("좋아요 요청 실패", err);
  }
};

</script>

<template>
  <button @click="() => router.back()" class="back-btn">
    <img src="@/components/icon/LeftArrow.svg" alt="뒤로가기" style="width: 20px;" />
  </button>
  <div v-if="news" class="news-detail">
    <div class="article__container">
      <ContentBox>
        <div class="article">
          <div class="article__header">
            <StateButton type="state" size="sm" isActive disabled>{{
              news?.category
            }}</StateButton>
            <h2 class="article__header-title">{{ news?.title }}</h2>
            <div class="article__header-writer">
              <span>{{ news.writer }}</span>
              <span> 🕒 {{ formatDate(news.write_date) }}</span>
            </div>
          </div>

          <p class="article__content">{{ news?.content }}</p>

          <div class="article__tags">
            <StateButton
              v-for="(tag, index) in news.keywords"
              :key="index"
              type="tag"
              size="sm"
            >
              {{ tag }}
            </StateButton>
          </div>

          <div class="article__content__footer">
            <div class="article__content__emoji">
              <div class="emoji-btn">
                <span v-if="liked">❤️</span>
                <span v-else>🤍</span>
                {{ likeCount }}
              </div>
              <div class="emoji-btn">
                <span class="content__emoji-eye">👀</span>
                {{ news?.views }}
              </div>
              <a :href="news.url">📄</a>
            </div>
            <button class="emoji-btn" @click="toggleLike">
              <span>{{ liked ? "❤️" : "🤍" }} 좋아요</span>
            </button>
            <!-- 애니메이션 하트 -->
            <transition name="heart-float">
              <span v-if="isAnimating" class="floating-heart">
                {{ liked ? "❤️" : "🤍" }}
              </span>
            </transition>
          </div>
        </div>
      </ContentBox>
    </div>

    <ContentBox class="sidebar">
      <h1 class="sidebar__title">📰 관련 기사</h1>
      <div
        v-for="(item, index) in relatedNews"
        :key="item.id"
      >
        <ArticlePreview
          :to="`/news/${item.id}`"
          :news="item"
        />
      </div>
    </ContentBox>
  </div>
</template>

<style scoped lang="scss">
.back-btn {
  margin-bottom: 10px;
}

.news-detail {
  display: flex;
  gap: 20px;

  @media (max-width: 800px) {
    flex-direction: column;
  }

  .article__container {
    flex: 2;
    display: flex;
    flex-direction: column;
    gap: 50px;
  }

  .sidebar {
    flex: 1;
    &__title {
      font-weight: 700;
      font-size: 18px;
      margin-bottom: 20px;
    }
  }

  .article {
    font-size: 1rem;
    padding: 20px;
    &__header {
      color: #888;
      font-size: 0.9rem;
      margin-bottom: 10px;
      &-title {
        margin: 12px 0;
        font-size: 1.6rem;
        font-weight: bold;
        color: #1c1c1e;
      }
      &-writer {
        display: flex;
        gap: 10px;
      }
    }

    &__content {
      margin: 16px 0;
      line-height: 1.6;

      &__footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
      }

      &__emoji {
        color: #888;
        font-size: 16px;
        display: flex;
        gap: 30px;
        align-items: center;
        &-eye {
          font-size: 17px;
        }
      }
    }

    &__tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 15px;
    }
  }

  .emoji-btn {
    display: flex;
    align-items: center;
    font-size: 15px;
    color: #888;
  }

  .floating-heart {
    position: absolute;
    font-size: 24px;
    color: red;
    animation: heartFloat 0.6s ease-out forwards;
  }

  @keyframes heartFloat {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    50% {
      opacity: 0.8;
      transform: translateY(-20px) scale(1.2);
    }
    100% {
      opacity: 0;
      transform: translateY(-40px) scale(0.8);
    }
  }
}
</style>
