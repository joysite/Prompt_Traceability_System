import axios from 'axios'

const API_BASE_URL = '/api'

const instance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // token 失效或未登录，清理并跳转登录
      localStorage.removeItem('admin_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default instance
