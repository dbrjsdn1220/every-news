<script setup>
import { ref, onMounted, watch } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import ArticlePreview from "@/components/ArticlePreview.vue";
import ChatBotToggle from "@/components/ChatBotToggle.vue";
import { useRoute, useRouter } from "vue-router";
import api from "@/utils/axios";
import HighlightableText from "@/components/HighlightableText.vue";

const route = useRoute();
const router = useRouter();
const { formatDate } = useDate();

const news = ref();
const relatedNews = ref([]);
const liked = ref(false);
const likeCount = ref(0);
const isAnimating = ref(false);
const searchQuery = ref("");
const highlights = ref([]);
const comments = ref([]);
const newCommentText = ref("");

const goBack = () => {
  router.back();
};

async function fetchDetail() {
  const { id } = route.params;
  try {
    // 기사 상세 조회
    const res = await api.get(`/api/news/${id}/`);
    news.value = res.data.data;
    likeCount.value = res.data.data.like_count ?? 0;

    // 좋아요 여부는 따로 판단 필요 → liked 초기값 false로 두고, 개선 가능
    liked.value = res.data.liked;

    // 관련 기사 조회
    const relatedRes = await api.get(`/api/news/${id}/related/`);
    relatedNews.value = relatedRes.data;

    // 댓글 조회
    const commentRes = await api.get(`/api/news/${id}/commented/`);
    comments.value = commentRes.data;
    console.log('Fetched comments:', comments.value);
  } catch (err) {
    console.error("초기 데이터 로딩 실패:", err);
  }
}

///////////////////////////////////////////////////////////////////// 하이라이트
// 하이라이트 목록 가져오기
const fetchHighlights = async () => {
  if (!localStorage.getItem('access')) return;
  
  try {
    const res = await api.get(
      `/api/news/${route.params.id}/highlighted/`,
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('access')}`
        }
      }
    );
    highlights.value = res.data;
  } catch (error) {
    console.error('하이라이트 목록 가져오기 실패:', error);
  }
};

// 하이라이트 생성 이벤트 처리
const handleHighlightCreated = (newHighlight) => {
  // 기존 목록에 새로 생성된 하이라이트 추가
  highlights.value.push(newHighlight);
  // console.log('현재 하이라이트 목록 (생성 후):', highlights.value.map(h => h.id));
};

// 하이라이트 삭제 이벤트 처리
const handleHighlightDeleted = (highlightId) => {
  // 해당 ID를 가진 하이라이트를 목록에서 제거
  const initialCount = highlights.value.length;
  highlights.value = highlights.value.filter(h => {
      // ID를 문자열로 변환하여 비교
      const isMatch = String(h.id) === String(highlightId);
      return !isMatch; // 일치하지 않는 항목만 남김
  });
  const finalCount = highlights.value.length;
  
};

onMounted(() => {
  fetchDetail();
  fetchHighlights(); // 페이지 로드 시 기존 하이라이트 불러오기
});

// 라우트 파라미터(id)가 바뀔 때마다 데이터 다시 불러오기
watch(() => route.params.id, () => {
  fetchDetail();
  fetchHighlights();
});

/////////////////////////////////////////////////////////////////////// 좋아요 기능
const toggleLike = async () => {
  const { id } = route.params;
  try {
    const res = await api.post(`/api/user/like/${id}/`, {}, {
      headers: {
        Authorization: `Token ${localStorage.getItem("access")}`,
      },
    });
    likeCount.value = res.data.like_count;
    liked.value = !liked.value;
  } catch (err) {
    alert("로그인이 필요합니다.");
    console.error("좋아요 처리 실패:", err);
  }
};

// 댓글 작성
const addComment = async () => {
  const { id } = route.params;
  if (!newCommentText.value.trim()) {
    alert('댓글 내용을 입력해주세요.');
    return;
  }
  try {
    const res = await api.post(
      `/api/user/comment/${id}/`,
      { comment: newCommentText.value },
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('access')}`
        }
      }
    );
    // 댓글 목록 새로고침
    const commentRes = await api.get(`/api/news/${id}/commented/`);
    comments.value = commentRes.data;
    newCommentText.value = ''; // 입력 필드 초기화
    console.log('Comment added:', res.data);
  } catch (error) {
    console.error('댓글 생성 실패:', error);
    alert('댓글 작성에 실패했습니다. 로그인 상태를 확인해주세요.');
  }
};

</script>

<template>
  <div class="news-detail-view-container">
    <div class="header__container">
      <header>
        <!-- 기존 로고/메뉴 등 -->
        <div style="flex:1"></div>
        <SearchBar />
        <!-- 기존 메뉴 등 -->
      </header>
    </div>
    <button @click="goBack" class="back-btn">
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

            <div class="article__content">
              <HighlightableText
                :text="news?.content"
                :article-id="route.params.id"
                :highlights="highlights"
                @highlight-created="handleHighlightCreated"
                @highlight-deleted="handleHighlightDeleted"
              />
            </div>

            <div class="article__tags">
              <StateButton
                v-for="(tag) in news.keywords"
                :key="tag"
                type="tag"
                size="sm"
              >
                #{{ tag }}
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
                <div class="emoji-btn">
                  <span >💬</span>
                  {{ news?.comment_count }}
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

        <!-- 댓글 부분 -->
        <ContentBox>
          <div class="comment-section">
            <h3>댓글 ({{ comments.length }})</h3>
            <div class="comment-list">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-header">
                  <strong>{{ comment.username }}</strong>
                  <span>{{ formatDate(comment.commented_at) }}</span>
                </div>
                <p>{{ comment.comment }}</p>
              </div>
            </div>
            <div class="comment-form">
              <textarea 
                v-model="newCommentText" 
                placeholder="댓글을 입력하세요..."
                rows="3"
              ></textarea>
              <button @click="addComment">댓글 작성</button>
            </div>
          </div>
        </ContentBox>

      </div>
      <!-- 관련 기사 -->
      <ContentBox class="sidebar">
        <h1 class="sidebar__title">📰 관련 기사</h1>
        <div v-for="(item) in relatedNews" :key="item.id">
          <ArticlePreview :news="item" :to="`/api/news/${item.id}`" />
        </div>
      </ContentBox>
    </div>
    <div>
      <ChatBotToggle />
    </div>
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
    gap: 20px;
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
      margin: 20px 0;
      font-size: 1.1rem;
      line-height: 1.8;
      color: #333;

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

.news-detail-view-container {
  // Add any necessary styles for the wrapper
}

.comment-section {
  margin-top: 10px;
  h3 {
    margin-bottom: 15px;
    font-size: 1.3rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
  }
}

.comment-list {
  margin-bottom: 0px;
}

.comment-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #f9f9f9;
  .comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    strong {
      font-size: 1rem;
    }
    span {
      font-size: 0.85rem;
      color: #777;
    }
  }
  p {
    font-size: 0.95rem;
    line-height: 1.5;
    color: #333;
  }
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
    resize: vertical;
    box-sizing: border-box;
  }
  button {
    align-self: flex-end;
    padding: 10px 20px;
    background-color: #272c97;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    &:hover {
      background-color: #272c97;
    }
  }
}
</style>
