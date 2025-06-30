import { io } from 'socket.io-client'

let socket = null
let singleListeners = []
let singleImageListeners = []
let groupListeners = []
let groupImageListeners = []

function connect(userId) {
  if (socket) return
  socket = io(import.meta.env.VITE_SOCKET_URL || 'http://127.0.0.1:5000', {
    query: { user_id: userId }
  })
  socket.on('connect', () => console.log('socket.io 已连接'))
  socket.on('disconnect', () => console.log('socket.io 已断开'))

  // 单聊消息
  socket.on('single_message', (msg) => {
    singleListeners.forEach(fn => fn(msg))
  })
  socket.on('single_image', (msg) => {
    singleImageListeners.forEach(fn => fn(msg))
  })

  // 群聊消息
  socket.on('group_message', (msg) => {
    groupListeners.forEach(fn => fn(msg))
  })
  socket.on('group_image', (msg) => {
    groupImageListeners.forEach(fn => fn(msg))
  })
}

// 发送单聊文字
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
// 发送单聊图片
function sendSingleImage({ from, to, image, filename, extra }) {
  if (socket && socket.connected) {
    socket.emit('single_image', {
      from,
      to,
      image,
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

// 群聊
function sendGroupMessage({ from, group_id, content, ...rest }) {
  if (socket && socket.connected) {
    socket.emit('group_message', {
      from,
      group_id,
      content,
      msg_type: 'text',
      send_time: Date.now(),
      ...rest
    })
  }
}
function sendGroupImage({ from, group_id, image, filename, extra, ...rest }) {
  if (socket && socket.connected) {
    socket.emit('group_image', {
      from,
      group_id,
      image,
      filename,
      msg_type: 'image',
      send_time: Date.now(),
      extra,
      ...rest
    })
  }
}
function onGroupMessage(fn) {
  groupListeners.push(fn)
}
function offGroupMessage(fn) {
  groupListeners = groupListeners.filter(f => f !== fn)
}
function onGroupImage(fn) {
  groupImageListeners.push(fn)
}
function offGroupImage(fn) {
  groupImageListeners = groupImageListeners.filter(f => f !== fn)
}

function close() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
  // 清空所有监听
  singleListeners = []
  singleImageListeners = []
  groupListeners = []
  groupImageListeners = []
}

export default {
  connect,
  sendSingleMessage,
  sendSingleImage,
  onSingleMessage,
  offSingleMessage,
  onSingleImage,
  offSingleImage,
  close,
  sendGroupMessage,
  sendGroupImage,
  onGroupMessage,
  offGroupMessage,
  onGroupImage,
  offGroupImage
}