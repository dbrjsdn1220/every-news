import axios from "axios";

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: "http://localhost:8000",  // Django 서버 주소
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem("access");
    if (accessToken) {
      config.headers.Authorization = `Token ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;