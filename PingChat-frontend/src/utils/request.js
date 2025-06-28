import axios from 'axios'

const request = axios.create({
  // 你可以在这里配置 baseURL、timeout、headers 等
  baseURL: '/', // 根据实际项目配置
  timeout: 10000
})

export default request