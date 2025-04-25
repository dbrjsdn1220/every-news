<template>
    <div class="register">
      <h2>회원가입</h2>
      <form @submit.prevent="register">
        <input v-model="username" placeholder="아이디" required />
        <input v-model="password1" type="password" placeholder="비밀번호" required />
        <input v-model="password2" type="password" placeholder="비밀번호 확인" required />
        <button type="submit">회원가입</button>
      </form>
      <p v-if="error">{{ error }}</p>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import api from "@/utils/axios";
  import router from "@/router";
  
  const username = ref("");
  const password1 = ref("");
  const password2 = ref("");
  const error = ref("");
  
  const register = async () => {
    if (password1.value !== password2.value) {
      error.value = "비밀번호가 일치하지 않습니다.";
      return;
    }
  
    try {
        await api.post("http://localhost:8000/accounts/signup/", {
            username: username.value,
            password: password1.value,
            });

      alert("회원가입 성공!");
      router.push("/login");
    } catch (err) {
      error.value = "회원가입에 실패했습니다.";
      console.error(err);
      console.log("회원가입 전송 데이터:", {
        username: username.value,
        password: password1.value
        });
    }
  };
  </script>
  
  <style scoped>
  .register {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 80px;
  }
  input {
    margin: 8px;
    padding: 8px;
    width: 250px;
  }
  button {
    padding: 10px 20px;
    margin-top: 12px;
  }
  </style>
  