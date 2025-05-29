<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const isOpen = ref(false);
const message = ref("");
const chatHistory = ref([]);
const isLoading = ref(false);
const error = ref('');

const articleId = computed(() => route.params.id);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
};

const resetChat = async () => {
  try {
    await axios.post(
      `/api/chatbot/${articleId.value}/reset/`,
      {},
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('access')}`,
        },
      }
    );
    chatHistory.value = [];
    error.value = '';
  } catch (err) {
    error.value = '채팅 초기화 중 오류가 발생했습니다.';
    console.error('Reset error:', err);
  }
};


// send_message
const sendMessage = async () => {
  if (!message.value.trim()) return;
  
  const userMessage = message.value.trim();
  message.value = "";  
  
  // 사용자 메시지 추가
  chatHistory.value.push({
    role: 'user',
    content: userMessage
  });
  
  isLoading.value = true;
  error.value = '';
  
  try {
    const response = await axios.post(
      `/api/chatbot/${articleId.value}/`,
      { question: userMessage },
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('access')}`,
        },
      }
    );

    // 챗봇 응답 추가
    chatHistory.value.push({
      role: 'assistant',
      content: response.data.response
    });
  } catch (err) {
    error.value = '메시지 전송 중 오류가 발생했습니다.';
    console.error('Chat error:', err);
    
    // 에러 메시지 추가
    chatHistory.value.push({
      role: 'assistant',
      content: '죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.'
    });
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="chatbot-toggle-container">
    <div v-if="isOpen" class="chat-window">
      <div class="chat-header">
        <strong>📰 뉴스 챗봇</strong>
        <div class="header-buttons">
          <button @click="resetChat" class="reset-btn" title="대화 초기화">🔄</button>
          <button @click="toggleChat" class="close-btn">✖</button>
        </div>
      </div>

      <div class="chat-body">
        <div class="chat-history">
          <template v-if="chatHistory.length === 0">
            <p class="welcome-message">뉴스 기사에 대해 궁금한 점을 물어보세요!</p>
          </template>
          <template v-else>
            <div v-for="(msg, index) in chatHistory" :key="index" 
                 :class="['message', msg.role === 'user' ? 'user-message' : 'bot-message']">
              <div class="message-content">
                {{ msg.content }}
              </div>
            </div>
          </template>
          <div v-if="isLoading" class="loading-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </div>
      </div>

      <div class="chat-input-row">
        <input
          v-model="message"
          type="text"
          placeholder="궁금한 점을 입력하세요"
          @keyup.enter="sendMessage"
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading || !message.trim()">
          {{ isLoading ? '전송 중...' : '전송' }}
        </button>
      </div>
    </div>

    <button v-if="!isOpen" class="chatbot-btn" @click="toggleChat">
      💬 챗봇 질문하기
    </button>
  </div>
</template>

<style scoped>
.chatbot-toggle-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
}

.chatbot-btn {
  background-color: #272c97;
  color: white;
  border: none;
  padding: 14px 20px;
  border-radius: 50px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.chat-window {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 400px;
  height: 400px;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.chat-header {
  background-color: #272c97;
  color: white;
  padding: 12px;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.chat-input-row {
  display: flex;
  margin-top: 12px;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #eee;
}

.chat-input-row input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.chat-input-row button {
  background-color: #272c97;
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
}

.header-buttons {
  display: flex;
  gap: 8px;
}

.reset-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
}

.reset-btn:hover {
  opacity: 0.8;
}

.chat-history {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  margin: 4px 0;
}

.user-message {
  align-self: flex-end;
  background-color: #272c97;
  color: white;
}

.bot-message {
  align-self: flex-start;
  background-color: #f0f0f0;
  color: #333;
}

.welcome-message {
  text-align: center;
  color: #666;
  margin: 20px 0;
}

.loading-indicator {
  display: flex;
  justify-content: center;
  gap: 4px;
  padding: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #272c97;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.error-message {
  color: #dc3545;
  text-align: center;
  padding: 8px;
  background-color: #f8d7da;
  border-radius: 4px;
  margin: 8px 0;
}

.chat-input-row input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.chat-input-row button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
