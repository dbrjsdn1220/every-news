<script setup>
import { Bar, Doughnut } from "vue-chartjs";
import { onMounted } from "vue";
import api from "@/utils/axios";
import dayjs from "dayjs";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import ContentBox from "@/common/ContentBox.vue";
import { ref } from "vue";
import ArticlePreview from "@/components/ArticlePreview.vue";
import duration from 'dayjs/plugin/duration';
import weekday from 'dayjs/plugin/weekday';
import isoWeek from 'dayjs/plugin/isoWeek';

dayjs.extend(duration);
dayjs.extend(weekday);
dayjs.extend(isoWeek);

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

const props = defineProps();
//////////////////////////////////////////////////////////////////// 나의 관심 카테고리
const categories = ref([]);
const categoryData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: [],
    },
  ],
});

// ** 추가: 독서 통계 상태 변수 **
const currentMonthReadCount = ref(0);
const lastMonthReadCount = ref(0);
const currentMonth = ref(dayjs().format('M월'));
const lastMonth = ref(dayjs().subtract(1, 'month').format('M월'));


const options = {
  plugins: {
    legend: {
      display: true,
      position: "right",
      labels: {
        padding: 15,
        boxWidth: 20,
        font: {
          size: 14,
        },
      },
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          return `${label}: ${value}개`;
        },
      },
    },
    layout: {
      padding: {
        right: 40,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        min: 0,
        max: 1,
      },
    },
  },
};

function generateColors(count) {
  const colors = [];
  const saturation = 70;
  const lightness = 60;

  for (let i = 0; i < count; i++) {
    const hue = Math.round((360 * i) / count);
    colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
  }
  return colors;
}


// ** 독서 목표치 상수 **
const READING_GOAL = 100; // 이번 달 독서 목표

// ** 독서 캘린더 상태 변수 및 선택된 날짜/기사 상태 **
const readingCalendar = ref([]);
const calendarMonthYear = ref(dayjs().format('YYYY년 M월'));

const selectedCalendarDate = ref(null); // 선택된 날짜 (dayjs 객체)
const articlesOnSelectedDate = ref([]); // 선택된 날짜에 읽은 기사 목록


// ** 독서 캘린더 데이터 생성 함수 (viewLogs 포함) **
const generateReadingCalendar = (viewLogs) => {
  const now = dayjs();
  const startOfMonth = now.startOf('month');
  const endOfMonth = now.endOf('month');
  
  // Group viewLogs by day of the month
  const dailyViewLogs = {};
  viewLogs.forEach(log => {
    const viewDate = dayjs(log.viewed_at);
    if (viewDate.isSame(now, 'month')) {
      const dayOfMonth = viewDate.date();
      if (!dailyViewLogs[dayOfMonth]) {
        dailyViewLogs[dayOfMonth] = [];
      }
      dailyViewLogs[dayOfMonth].push(log);
    }
  });
  
  // Create calendar days array
  const daysInMonth = endOfMonth.date();
  const firstDayOfWeek = startOfMonth.weekday(); // 0 for Sunday, 1 for Monday, etc.

  const calendarDays = [];
  
  // Add empty slots for days before the 1st
  for (let i = 0; i < firstDayOfWeek; i++) {
    calendarDays.push({ date: null, count: 0, logs: [] });
  }
  
  // Add days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const logsForDay = dailyViewLogs[day] || [];
    const uniqueArticles = new Set(logsForDay.map(log => log.article.id));
    
    calendarDays.push({
      date: day,
      count: uniqueArticles.size,
      logs: logsForDay // 해당 날짜의 전체 viewLogs 저장
    });
  }
  
  readingCalendar.value = calendarDays;
};

// ** 추가: 날짜 선택 핸들러 **
const selectCalendarDate = (day) => {
  if (day.date) { // 유효한 날짜인 경우에만 선택
    const selectedDateObj = dayjs().date(day.date); // 현재 월/년 기준으로 날짜 객체 생성
    selectedCalendarDate.value = selectedDateObj;
    // 중복 기사 제거하고 목록 업데이트
    const articleMap = new Map();
    day.logs.forEach(log => {
        articleMap.set(log.article.id, log.article);
    });
    articlesOnSelectedDate.value = Array.from(articleMap.values());
    console.log(`선택된 날짜: ${selectedDateObj.format('YYYY-MM-DD')}, 읽은 기사 수: ${articlesOnSelectedDate.value.length}`);
  } else {
    selectedCalendarDate.value = null;
    articlesOnSelectedDate.value = [];
  }
};

// ** 추가: 사용자 정보 상태 변수 **
const userName = ref(localStorage.getItem("username") || '사용자'); // localStorage에서 가져오고 없으면 '사용자'로 설정
const userHighlightCount = ref(0);
const userCommentCount = ref(0);
const userLikeCount = ref(0);
const userAttendCount = ref(0);


onMounted(async () => {
  // 하이라이트 개수, 좋아요 개수, 댓글 개수 가져오기
  try {
    const userInfo = await api.get('/api/user/information/', {
      headers: {
        Authorization: `Token ${localStorage.getItem("access")}`,
      },
    });
    userHighlightCount.value = userInfo.data.total_highlight;
    userCommentCount.value = userInfo.data.total_comment;
    userLikeCount.value = userInfo.data.total_like;
    userAttendCount.value = userInfo.data.total_attendance;
  } catch (err) {
    console.error("가져오기 실패:", err);
  }

  try {
    const res = await api.get("/api/user/viewed/", {
      headers: {
        Authorization: `Token ${localStorage.getItem("access")}`,
      },
    });

    const viewLogs = res.data;

    // 카테고리별 카운팅
    const categoryCount = {};
    viewLogs.forEach((log) => {
      const category = log.article.category;
      if (category) {
        categoryCount[category] = (categoryCount[category] || 0) + 1;
      }
    });

    // 등장 수 기준 정렬 후 상위 순위만 뽑기
    const sorted = Object.entries(categoryCount).sort((a, b) => b[1] - a[1]);
    console.log('sorted:' ,sorted)
    const autoColors = generateColors(sorted.length);
    console.log(autoColors)

    // 차트 데이터 구성
    categoryData.value.labels = sorted.map(([label]) => label);
    categoryData.value.datasets[0].data = sorted.map(([, count]) => count);
    categoryData.value.datasets[0].backgroundColor = autoColors;
    console.log('category : ', categoryData.value)

    // 하단 순위 텍스트용
    categories.value = sorted.slice(0, 3); // TOP 3만 추출
  } catch (err) {
    console.error("카테고리 분석 실패", err);
  }
});

////////////////////////////////////////////////////////////////////////// 주요 키워드
onMounted(async () => {
  try {
    const res = await api.get("/api/user/viewed/", {
      headers: {
        Authorization: `Token ${localStorage.getItem("access")}`,
      },
    });

    const viewLogs = res.data;

    const keywordFreq = {};

    viewLogs.forEach((log) => {
      const keywords = log.article.keywords || [];
      keywords.forEach((kw) => {
        const trimmed = kw.trim();
        if (trimmed) {
          keywordFreq[trimmed] = (keywordFreq[trimmed] || 0) + 1;
        }
      });
    });

    // 등장 빈도순으로 정렬 → 상위 5개 추출
    const sortedKeywords = Object.entries(keywordFreq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    // 차트에 반영
    keywordData.value.labels = sortedKeywords.map(([kw]) => kw);
    keywordData.value.datasets[0].data = sortedKeywords.map(([, count]) => count);

  } catch (err) {
    console.error("키워드 분석 실패", err);
  }
});


const keywordData = ref({
  labels: [],
  datasets: [
    {
      label: "키워드 빈도수",
      data: [],
      backgroundColor: "#C7E4B8",
    },
  ],
});


const barOptions = {
  indexAxis: "y",
  scales: {
    x: {
      beginAtZero: true,
    },
  },
  plugins: {
    legend: {
      display: false,
    },
  },
};


////////////////////////////////////////////////////////////// 일주일간 조회한 기사 개수
onMounted(async () => {
  if (!isLoggedIn.value) return;

  try {
    const res = await api.get("/api/user/viewed/");

    const viewLogs = res.data; // 전체 읽은 기록

    // 월별 독서량 계산
    const now = dayjs();
    const currentMonthLogs = viewLogs.filter(log =>
      dayjs(log.viewed_at).isSame(now, 'month')
    );
    const lastMonthLogs = viewLogs.filter(log =>
      dayjs(log.viewed_at).isSame(now.subtract(1, 'month'), 'month')
    );
    
    const uniqueCurrentMonthArticles = new Set(currentMonthLogs.map(log => log.article.id));
    const uniqueLastMonthArticles = new Set(lastMonthLogs.map(log => log.article.id));

    currentMonthReadCount.value = uniqueCurrentMonthArticles.size;
    lastMonthReadCount.value = uniqueLastMonthArticles.size;

    // 독서 캘린더 데이터 생성
    generateReadingCalendar(viewLogs); // viewLogs 전체를 전달

    // 일주일간 조회한 기사 개수
    const past7Days = [...Array(7)].map((_, i) =>
      now.subtract(6 - i, "day").format("MM-DD")
    );
    const viewCountPerDay = Object.fromEntries(
      past7Days.map((date) => [date, 0])
    );
    
    // 주간 읽은 기사 개수 계산
    viewLogs.forEach((log) => {
      const viewedDate = dayjs(log.viewed_at).format("MM-DD");
      if (viewedDate in viewCountPerDay) {
        viewCountPerDay[viewedDate]++;
      }
    });
    
    readData.value.labels = past7Days;
    readData.value.datasets[0].data = past7Days.map(
      (date) => viewCountPerDay[date]
    );

  } catch (err) {
    console.error("읽은 기록 불러오기 실패:", err);
  }
});

const readData = ref({
  labels: [],
  datasets: [
    {
      label: "읽은 기사 개수",
      data: [],
      backgroundColor: "#DBB8E4",
    },
  ],
});

const readBarOptions = {
  indexAxis: "x",
  scales: {
    x: {
      beginAtZero: true,
    },
  },
  plugins: {
    legend: {
      display: false,
    },
  },
};


////////////////////////////////////////////////////////////// 좋아요한 기사 목록 찾아보기
const isLoggedIn = ref(!!localStorage.getItem("access"));
const favoriteArticles = ref([]);

onMounted(async () => {
  if (!isLoggedIn.value) return;

    try {
      const response = await api.get("/api/user/liked/" , {
        headers: {
          Authorization: `Token ${localStorage.getItem("access")}`,
        },
      });
      favoriteArticles.value = response.data;
    } catch (error) {
      console.error("좋아요 기사 불러오기 실패", error);
  }
});

</script>

<template>
  <div class="dashboard-container">
    <div class="dashboard">
      <h1 class="title">내 서재</h1>
      <p class="subtitle">
        <br />방문 기록 및 좋아요 데이터를 기반으로 나의 관심 분야를 확인하고,
        <br />관심 분야에 맞는 기사를 추천 받아보세요. <br />여러분의 취업 여정의
        로드맵을 제공합니다.
      </p>

      <!-- 사용자 정보 섹션 -->
      <ContentBox class="user-info-section content-box">
        <div class="user-info-header">
          <img src="@/assets/profile.jpg" alt="프로필 이미지" width="200" class="profile-image"/>
          <div class="user-details">
            <h2>
              <div v-if="userName">
                <h1> {{ userName }} 님 </h1>
              </div>
            </h2>
          </div>
        </div>
        <div class="user-stats">
          <div class="stat-item">
            <strong>{{ userHighlightCount }}</strong>
            <small>하이라이트</small>
          </div>
          <div class="stat-item">
            <strong>{{ userCommentCount }}</strong>
            <small>댓글</small>
          </div>
          <div class="stat-item">
            <strong>{{ userLikeCount }}</strong>
            <small>좋아요</small>
          </div>
           <div class="stat-item">
            <strong>{{ userAttendCount }}</strong>
            <small>출석</small>
          </div>
        </div>
      </ContentBox>

      <!-- 독서 통계 섹션 -->
      <ContentBox class="reading-stats">
        <div class="reading-stats__header">
          <h1>이번 달 {{ currentMonthReadCount }}개의 기사를 읽었어요😊</h1>
          <p>목표까지 {{100 - currentMonthReadCount}}개의 기사가 남았어요! 좀만 더 힘내봐요!</p>
          <p>지난달보다 {{ Math.abs(currentMonthReadCount - lastMonthReadCount) }}개 {{ currentMonthReadCount >= lastMonthReadCount ? '더' : '덜' }} 읽고 있어요</p>
        </div>
        <div class="reading-stats__bars">
          <div class="stat-item">
            <span class="month-label">{{ currentMonth }}</span>
            <div class="progress-bar">
              <!-- 목표 달성 기준 바 -->
              <div 
                class="progress-bar__fill--goal-bg"
                :style="{ width: '100%' }"
              ></div>
              <!-- 목표 달성 바 (실제 진행률) -->
              <div 
                class="progress-bar__fill--goal"
                :style="{ width: `${Math.min((currentMonthReadCount / READING_GOAL) * 100, 100)}%` }"
              ></div>
              <!-- 현재 달 독서량 바 (비교용) -->
              <div 
                class="progress-bar__fill current-month"
                :style="{ width: `${(currentMonthReadCount / Math.max(currentMonthReadCount, lastMonthReadCount, 1)) * 100}%` }"
              ></div>
              
              <!-- 목표 달성 이모지 -->
              <span 
                class="goal-emoji"
                :style="{ left: `${Math.min((currentMonthReadCount / READING_GOAL) * 100, 100)}%` }"
              >🐤</span>
              
            </div>
            <span class="read-count">{{ currentMonthReadCount }}개 / 100개</span>
          </div>
          <div class="stat-item">
            <span class="month-label">{{ lastMonth }}</span>
            <div class="progress-bar">
              <div 
                class="progress-bar__fill last-month"
                :style="{ width: `${(lastMonthReadCount / Math.max(currentMonthReadCount, lastMonthReadCount, 1)) * 100}%` }"
              ></div>
            </div>
            <span class="read-count">{{ lastMonthReadCount }}개 / 100개</span>
          </div>
        </div>
      </ContentBox>

      <div class="calendar-and-articles-layout">
        <!-- 독서 캘린더 섹션 -->
        <ContentBox class="reading-calendar">
          <h2>{{ calendarMonthYear }} 기사 캘린더</h2>
          <div class="calendar-grid">
            <div class="calendar-header">
              <span>일</span>
              <span>월</span>
              <span>화</span>
              <span>수</span>
              <span>목</span>
              <span>금</span>
              <span>토</span>
            </div>
            <div class="calendar-body">
              <div 
                v-for="(day, index) in readingCalendar"
                :key="index"
                :class="['calendar-day', { 'empty': !day.date, 'has-reads': day.count > 0, 'selected': selectedCalendarDate && day.date && dayjs().date(day.date).isSame(selectedCalendarDate, 'day') }]"
                @click="selectCalendarDate(day)"
              >
                <span v-if="day.date">{{ day.date }}</span>
                <span v-if="day.count > 0" class="read-count-badge">{{ day.count }}</span>
              </div>
            </div>
          </div>
        </ContentBox>

        <!-- 선택된 날짜의 기사 목록 섹션 -->
        <ContentBox class="selected-articles">
          <h2>
            {{ selectedCalendarDate ? selectedCalendarDate.format('YYYY년 M월 D일') : '날짜를 선택하세요' }}
          </h2>
          <div v-if="selectedCalendarDate">
            <div v-if="articlesOnSelectedDate.length > 0" class="article-list">
              <ArticlePreview
                v-for="article in articlesOnSelectedDate"
                :key="article.id"
                :news="article"
                :to="`/api/news/${article.id}`"
              />
            </div>
            <p v-else>이 날짜에는 읽은 기사가 없습니다.</p>
          </div>
          <p v-else>캘린더에서 날짜를 선택하시면 읽은 기사 목록이 표시됩니다.</p>
        </ContentBox>
      </div>

      <div class="layout">
        <ContentBox class="category">
          <h1>🐤 나의 관심 카테고리</h1>
          <p class="card_description">
            내가 주로 읽은 기사들을 분석하여 정치, 경제, 문화 등 가장 관심 있는
            뉴스 카테고리를 한눈에 보여드립니다.
          </p>
          <div class="category__chart">
            <Doughnut v-if="categoryData.labels.length > 0" :data="categoryData" :options="options" />
            <div v-else class="no-data-message">읽은 기사가 없거나 카테고리 데이터가 없습니다.</div>
          </div>
           <!-- TOP 3 카테고리 목록 표시 (이미지 디자인 적용) -->
            <div class="top-categories-horizontal">
                <span
                    v-for="(category, index) in categories"
                    :key="index"
                    :style="{
                    borderColor: categoryData.datasets[0].backgroundColor[index],
                    color: categoryData.datasets[0].backgroundColor[index],
                    }"
                    class="top-category-item"
                >
                    {{ index + 1 }}위: {{ category[0] }} ({{ category[1] }}개)
                </span>
                 <span v-if="categories.length === 0 && categoryData.labels.length === 0" class="no-data-message-small">관심 카테고리 데이터가 없습니다.</span>
                 <span v-else-if="categories.length === 0" class="no-data-message-small">TOP 3 카테고리를 불러오는데 실패했습니다.</span>
            </div>
        </ContentBox>

        <ContentBox class="keyword">
          <h1>⭐️ 주요 키워드</h1>
          <p class="card_description">
            내가 관심있게 본 뉴스 기사들에서 가장 많이 등장한 핵심 키워드를
            추출하여 현재 나의 주요 관심사를 보여드립니다.
          </p>
          <Bar v-if="readData.labels.length > 0" :data="keywordData" :options="barOptions" />
        </ContentBox>
      </div>
      <div class="layout">
        <ContentBox>
          <h1>📰 주간 읽은 기사</h1>
          <p class="card_description">
            최근 일주일 동안 하루에 몇 개의 기사를 읽었는지 그래프로 확인하며 나의
            뉴스 소비 패턴을 분석합니다.
          </p>
          <Bar v-if="readData.labels.length > 0" :data="readData" :options="readBarOptions" />
          <p v-else>데이터를 불러오는 중입니다...</p>
        </ContentBox>

        <ContentBox class="like-news" v-if="isLoggedIn">
          <h1>❤️ 좋아요 누른 기사</h1>
          <p class="card_description">
            내가 좋아요를 누른 기사들의 목록을 한곳에서 모아보고 다시 찾아볼 수 있습니다.
          </p>
          <div v-if="favoriteArticles.length === 0">
            아직 좋아요한 기사가 없습니다.
          </div>
           <div v-else>
            <ArticlePreview
              v-for="articleWrapper in favoriteArticles"
              :key="articleWrapper.article.id"
              :to="`/api/news/${articleWrapper.article.id}`"
              :news="articleWrapper.article"
            />
          </div>
        </ContentBox>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard-container {
  max-width: 1280px; 
  margin: 0 auto;
  padding: 0 20px; 
}

.dashboard {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.title {
  font-size: 25px;
}
.subtitle {
  font-weight: 500;
}
.like-news {
  overflow-y: auto;
  box-sizing: border-box;
}

.card_description {
  margin: 10px;
}

.layout {
  display: flex;
  gap: 20px;
  > * {
    height: 450px;
  }

  @media (max-width: 768px) {
    flex-direction: column;
  }
}
.category {
  &__chart {
    height: 300px;
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 20px;
    padding-bottom: 0;
    justify-content: center; 

    > div:first-child {
        flex-shrink: 0;
        width: 200px;
    }
  }

}

.top-categories-horizontal {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px; 
    flex-wrap: wrap; 

    .top-category-item {
        border: 1px solid; 
        padding: 5px 12px; 
        border-radius: 20px; 
        font-size: 0.95rem; 
        font-weight: 500;
        white-space: nowrap; 
    }
     .no-data-message-small {
        font-size: 0.9rem;
        color: #666;
        text-align: center;
        width: 100%;
        margin-top: 10px;
     }
}


.reading-stats {

  &__header {
    h1 {
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 10px;
    }
    p {
      font-size: 0.9rem;
      color: #666;
      margin-bottom: 20px;
    }
  }

  &__bars {
    display: flex;
    flex-direction: column;
    gap: 15px;
    width: 100%;

    .stat-item {
      display: flex;
      align-items: center;
      gap: 15px;
      width: 100%;

      .month-label {
        font-weight: 600;
        width: 40px;
        text-align: right;
        flex-shrink: 0;
      }

      .progress-bar {
        width: 1000px;
        flex-shrink: 0;
        height: 20px;
        background-color: #eee;
        border-radius: 10px;
        overflow: hidden;
        position: relative;

        &__fill {
          position: absolute;
          top: 0;
          left: 0;
          height: 100%;
          border-radius: 10px;
          transition: width 0.5s ease-in-out;
        }

        &__fill--goal-bg {
            @extend .progress-bar__fill;
            background-color: #8a8dca7a;
            z-index: 1;
            width: 100%;
        }

        &__fill--goal {
            @extend .progress-bar__fill;
            background-color: #272c97;
            z-index: 1;
        }

        .last-month {
          @extend .progress-bar__fill;
          background-color: #b0b0b0;
          z-index: 1;
          width: 100%;
        }

         .goal-emoji {
            position: absolute;
            top: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            z-index: 3;
            pointer-events: none;
        }
      }

      .read-count {
        font-weight: 600;
        margin-left: 10px;
        white-space: nowrap;
        flex-shrink: 0;
      }
    }
  }
}

.calendar-and-articles-layout {
  display: flex;
  gap: 20px;

  @media (max-width: 900px) {
    flex-direction: column;
  }
}

.reading-calendar {
  flex: 1;
  max-width: 650px;
  margin: 0;
  
  h2 {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 15px;
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(auto-fit, minmax(45px, 1fr));
    gap: 5px;
    text-align: center;

    .calendar-header {
      display: contents;

      span {
        font-weight: 600;
        padding: 10px 0;
        border-bottom: 1px solid #eee;
      }
    }

    .calendar-body {
        display: contents;
    }

    .calendar-day {
      position: relative;
      padding: 8px 4px;
      border: 1px solid #eee;
      border-radius: 5px;
      aspect-ratio: 1 / 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      color: #555;
      cursor: pointer;
      transition: background-color 0.2s ease;

      &.empty {
        background-color: #f8f8f8;
        visibility: hidden;
        cursor: default;
      }
      
      &.selected {
        background-color: #cce5ff;
        border-color: #007bff;
        color: #004085;
        font-weight: bold;
      }

      &.has-reads {
        background-color: #e0f2f7;
        border-color: #b2ebf2;
        font-weight: bold;
        color: #555;
      }

      &:not(.empty):not(.selected):hover {
        background-color: #f0f0f0;
      }

      .read-count-badge {
        position: absolute;
        bottom: 2px;
        right: 2px;
        background-color: #272c97;
        color: white;
        font-size: 0.7rem;
        font-weight: bold;
        border-radius: 50%;
        padding: 0px 5px;
        min-width: 10px;
        text-align: center;
        line-height: 1.2;
      }
    }
  }
}

.selected-articles {
    flex: 1;

    h2 {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 15px;
        min-height: 1.2em;
    }
    
    .article-list {
        max-height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    p {
        color: #666;
        text-align: center;
        padding: 20px;
    }
}

.user-info-section.content-box {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    padding: 20px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 30px;

    @media (max-width: 768px) {
        flex-direction: column;
        align-items: flex-start;
    }
}

.user-info-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.profile-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #ccc;
}

.user-details h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #333;
}

.user-details p {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 0.9rem;
}

.user-stats {
  display: flex;
  gap: 30px;

  @media (max-width: 480px) {
    gap: 15px;
  }
}

.stat-item {
  text-align: center;

  strong {
    display: block;
    font-size: 1.4rem;
    font-weight: bold;
    color: #007bff;
  }

  small {
    font-size: 0.8rem;
    color: #555;
  }
}

.no-data-message {
    text-align: center;
    color: #666;
    font-size: 1rem;
    padding: 20px;
    width: 100%;
}
</style>
