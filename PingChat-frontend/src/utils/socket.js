import { io } from 'socket.io-client'

let socket = null
let singleListeners = []
let singleImageListeners = []

function connect(userId) {
  if (socket) return
  socket = io(import.meta.env.VITE_SOCKET_URL || 'http://127.0.0.1:5000', {
    query: { user_id: userId }
  })
  socket.on('connect', () => console.log('socket.io 已连接'))
  socket.on('disconnect', () => console.log('socket.io 已断开'))
  socket.on('single_message', (msg) => {
    singleListeners.forEach(fn => fn(msg))
  })
  socket.on('single_image', (msg) => {
    singleImageListeners.forEach(fn => fn(msg))
  })
}

function sendSingleMessage({ from, to, content }) {
  if (socket && socket.connected) {
    socket.emit('single_message', {
      from,
      to,
      content,
      msg_type: 'text',
      send_time: Date.now()
    })
  }
}

function sendSingleImage({ from, to, image, filename, extra }) {
  if (socket && socket.connected) {
    socket.emit('single_image', {
      from,
      to,
      image,        // base64字符串
      filename,
      msg_type: 'image',
      send_time: Date.now(),
      extra
    })
  }
}

function onSingleMessage(fn) {
  singleListeners.push(fn)
}
function offSingleMessage(fn) {
  singleListeners = singleListeners.filter(f => f !== fn)
}
function onSingleImage(fn) {
  singleImageListeners.push(fn)
}
function offSingleImage(fn) {
  singleImageListeners = singleImageListeners.filter(f => f !== fn)
}
function close() {
  if (socket) socket.disconnect()
  socket = null
}

export default {
  connect,
  sendSingleMessage,
  sendSingleImage,
  onSingleMessage,
  offSingleMessage,
  onSingleImage,
  offSingleImage,
  close
}