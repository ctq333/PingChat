// 简易版统一 WebSocket 工具
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:5000/ws' // 或你的实际 ws 地址

let socket = null
let reconnectTimer = null
let listeners = []

function connect(token, userId) {
  if (socket) return
  // 最常见的：token 作为 query 参数传到后端做鉴权
  const wsUrl = `${WS_URL}?token=${token}&user_id=${userId}`
  socket = new WebSocket(wsUrl)

  socket.onopen = () => {
    console.log('WebSocket 连接已建立')
  }
  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      listeners.forEach(fn => fn(msg))
    } catch (e) {
      console.warn('收到非 JSON 消息', event.data)
    }
  }
  socket.onclose = () => {
    console.warn('WebSocket 已断开，准备重连')
    socket = null
    // 自动重连
    reconnectTimer = setTimeout(() => {
      connect(token, userId)
    }, 2000)
  }
  socket.onerror = (err) => {
    console.error('WebSocket 错误', err)
  }
}

function send(obj) {
  if (socket && socket.readyState === 1) {
    socket.send(JSON.stringify(obj))
  } else {
    console.warn('WebSocket 未连接，消息未发送')
  }
}

// 订阅新消息
function onMessage(fn) {
  listeners.push(fn)
}

// 取消订阅
function offMessage(fn) {
  listeners = listeners.filter(l => l !== fn)
}

// 主动关闭
function close() {
  if (socket) {
    socket.close()
    socket = null
  }
}

export default {
  connect,
  send,
  onMessage,
  offMessage,
  close
}