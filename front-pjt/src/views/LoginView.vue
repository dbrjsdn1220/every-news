<template>
    <div class="auth-box">
      <h2>{{ isLogin ? "로그인" : "회원가입" }}</h2>
  
      <form @submit.prevent="isLogin ? login() : register()">
        <input v-model="username" type="text" placeholder="아이디" required />
        <input v-model="password1" type="password" placeholder="비밀번호" required />
        <input
          v-if="!isLogin"
          v-model="password2"
          type="password"
          placeholder="비밀번호 확인"
          required
        />
  
        <button type="submit">{{ isLogin ? "로그인" : "회원가입" }}</button>
      </form>
  
      <p class="error" v-if="error">{{ error }}</p>
  
      <p class="switch">
        {{ isLogin ? "계정이 없으신가요?" : "이미 계정이 있으신가요?" }}
        <span @click="toggleMode">
          {{ isLogin ? "회원가입" : "로그인" }}
        </span>
      </p>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import api from "@/utils/axios";
  import { useRouter } from "vue-router";
  
  const username = ref("");
  const password1 = ref("");
  const password2 = ref("");
  const isLogin = ref(true);
  const error = ref("");
  const router = useRouter();
  
  const toggleMode = () => {
    isLogin.value = !isLogin.value;
    error.value = "";
  };
  
  const login = async () => {
    try {
        const res = await api.post("http://localhost:8000/accounts/login/", {
        username: username.value,
        password: password1.value,
        });

        localStorage.setItem("access", res.data.access);
        localStorage.setItem("refresh", res.data.refresh);

        alert("로그인 성공");

        router.push("news/"); // 메인페이지로 이동
    } catch (err) {
        error.value = "아이디 또는 비밀번호가 올바르지 않습니다.";
    }
    };
    
  const register = async () => {
  if (password1.value !== password2.value) {
    error.value = "비밀번호가 일치하지 않습니다.";
    return;
  }

  try {
    const payload = {
        username: username.value,
        password1: password1.value,
        password2: password2.value,
        };

    console.log("보내는 데이터:", payload);  // 디버깅 로그

    await api.post("http://localhost:8000/accounts/signup/", payload);
    alert("회원가입 성공! 로그인 해주세요.");
    toggleMode();
  } catch (err) {
    console.error("회원가입 실패 응답:", err.response?.data || err);
    error.value = "회원가입에 실패했습니다.";
  }
};

  </script>
  
  <style scoped>
  .auth-box {
    max-width: 400px;
    margin: 100px auto;
    padding: 30px;
    border: 1px solid #ddd;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  }
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  form {
    display: flex;
    flex-direction: column;
  }
  input {
    margin-bottom: 10px;
    padding: 10px;
    font-size: 15px;
  }
  button {
    padding: 10px;
    background: #272c97;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  button:hover {
    background: #1d227e;
  }
  .switch {
    text-align: center;
    margin-top: 15px;
    font-size: 14px;
  }
  .switch span {
    color: #272c97;
    font-weight: bold;
    cursor: pointer;
    margin-left: 5px;
  }
  .error {
    color: red;
    text-align: center;
    margin-top: 10px;
  }
  </style>
  