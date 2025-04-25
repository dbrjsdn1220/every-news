import axios from "axios";

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: "http://localhost:8000",  // Django 서버 주소
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ 요청 인터셉터: 요청 보낼 때마다 토큰 자동 첨부
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem("access");
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;