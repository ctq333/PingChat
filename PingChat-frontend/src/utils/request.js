// src/utils/request.js
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const request = axios.create({
  baseURL: API_BASE_URL, // 自动加上你的后端地址
  timeout: 30000
})

export default request