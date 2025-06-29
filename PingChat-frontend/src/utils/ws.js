// utils/ws.js

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:5000/ws'

let socket = null
let reconnectTimer = null
let listeners = []

function connect(userId) {
  if (socket) return
  // 只带 user_id，不带 token
  const wsUrl = `${WS_URL}?user_id=${userId}`
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
    socket = null
    reconnectTimer = setTimeout(() => {
      connect(userId)
    }, 2000)
  }
  socket.onerror = (err) => {
    console.error('WebSocket 错误', err)
  }
}

function send(obj) {
  if (socket && socket.readyState === 1) {
    socket.send(JSON.stringify(obj))
  }
}

function onMessage(fn) {
  listeners.push(fn)
}
function offMessage(fn) {
  listeners = listeners.filter(l => l !== fn)
}
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