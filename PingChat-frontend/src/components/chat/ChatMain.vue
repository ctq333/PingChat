<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import request from '@/utils/request'
import socket from '@/utils/socket' 
import { saveImageToDB, getImageFromDB } from '@/utils/userChatStorage'
import { downloadMessageAsHTML } from '@/utils/export'
import GroupManageDialog from '@/components/group/GroupManageDialog.vue'




import IconSend from '~icons/material-symbols/send'
import IconImage from '~icons/material-symbols/image'
import IconClose from '~icons/material-symbols/close'
import IconDownload from '~icons/material-symbols/download'
import IconDelete from '~icons/material-symbols/delete'


const props = defineProps({
  chat: Object,
  currentUser: {
    type: Object,
  }
})

const messages = ref([])
const loading = ref(false)
const username = ref(null)
const showAddUserDialog = ref(false)

// 导出聊天记录为 HTML 文件，含图片
async function exportChatHistory() {
  // 取 user
  const userStr = localStorage.getItem('user')
  if (!userStr) {
    alert('请先登录')
    return
  }
  const currentUser = JSON.parse(userStr)
  const sender_id = currentUser.id

  // 取聊天对象id和类型
  if (!props.chat) {
    alert('无聊天对象')
    return
  }

  const { type, id } = props.chat

  // 准备请求参数
  const params = { sender_id }
  if (type === 'group') {
    params.group_id = id
  } else if (type === 'user') {
    params.receiver_id = id
  } else {
    alert('未知聊天类型')
    return
  }

  try {
    const resp = await request.get('/api/chat/export_chat_history', { params })
    if (resp.data.code !== 200) {
      alert('导出失败：' + resp.data.message)
      return
    }
    let messages = resp.data.data

    // ----------- 关键：处理图片消息 -----------
    // ----------- 补全每个图片消息的 content 为 base64 -----------
    messages = await Promise.all(messages.map(async msg => {
      // 兼容 type/msg_type
      const isImage = msg.type === 'image' || msg.msg_type === 'image'
      if (isImage) {
        // 1. 已经是 base64
        if (msg.content && msg.content.startsWith('data:image')) {
          return msg
        }
        // 2. 有 filename，尝试从indexedDB查base64
        if (msg.filename) {
          const base64 = await getImageFromDB(msg.filename)
          if (base64 && base64.startsWith('data:image')) {
            return { ...msg, content: base64 }
          } else {
            return { ...msg, content: '' } // 让下游变成“图片丢失”
          }
        }
        // 3. fallback：直接把内容清空（给下游生成“图片丢失”）
        return { ...msg, content: '' }
      }
      // 非图片消息直接返回
      return msg
    }))
    // ----------- 补全结束 -----------
    // ----------- 关键处理结束 -----------

    // 生成 HTML 内容
    const htmlContent = generateHtml(messages, type)

    // 触发浏览器下载
    downloadHtmlFile(htmlContent, `chat_history_${type}_${id}.html`)
  } catch (error) {
    alert('导出异常，请稍后重试')
  }
}

// 生成聊天HTML内容，messages是从接口拿到的数组
function generateHtml(messages, chatType) {
  // 现代化 CSS 样式
  const style = `
    <style>
      :root {
        --primary: #2563eb;
        --primary-light: #eef4ff;
        --bg: #f6f8fb;
        --bubble-user: #2563eb;
        --bubble-user-text: #fff;
        --bubble-other: #f3f4f6;
        --bubble-other-text: #222;
        --avatar-bg: #e0e7ff;
      }

      html, body {
        margin: 0; padding: 0;
        background: var(--bg);
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
        color: #222;
      }
      .chat-root {
        min-height: 100vh;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 0 40px 0;
      }
      .chat-container {
        width: 100%;
        max-width: 720px;
        background: #fff;
        margin: 40px auto 0 auto;
        border-radius: 18px;
        box-shadow: 0 4px 32px rgba(0,0,0,0.08);
        padding: 32px 0 0 0;
        overflow: hidden;
      }
      .chat-header {
        border-bottom: 1px solid #f3f4f6;
        padding: 0 32px 18px 32px;
        margin-bottom: 12px;
      }
      .chat-header h2 {
        margin: 0 0 4px 0;
        font-size: 1.4rem;
        font-weight: 700;
        color: #222;
      }
      .chat-header .type {
        font-size: 1rem;
        color: #888;
      }
      .chat-messages {
        padding: 0 32px;
        display: flex;
        flex-direction: column;
        gap: 24px;
        margin-bottom: 24px;
      }
      .msg-row {
        display: flex;
        align-items: flex-end;
        gap: 10px;
      }
      .msg-row.user {
        flex-direction: row-reverse;
      }
      .msg-avatar {
        width: 38px; height: 38px;
        border-radius: 50%;
        background: var(--avatar-bg);
        color: var(--primary);
        font-weight: 700;
        font-size: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 1px 5px rgba(0,0,0,0.07);
      }
      .msg-content {
        max-width: 68vw;
        min-width: 40px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
      }
      .msg-row.user .msg-content {
        align-items: flex-end;
      }
      .msg-meta {
        font-size: 0.83em;
        color: #949fb2;
        margin-bottom: 3px;
        display: flex;
        gap: 8px;
        align-items: center;
      }
      .msg-bubble {
        border-radius: 16px 16px 16px 3px;
        padding: 11px 17px;
        font-size: 1.05em;
        line-height: 1.6;
        word-break: break-word;
        background: var(--bubble-other);
        color: var(--bubble-other-text);
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 2px;
        transition: background .2s;
      }
      .msg-row.user .msg-bubble {
        background: var(--bubble-user);
        color: var(--bubble-user-text);
        border-radius: 16px 16px 3px 16px;
      }
      .msg-bubble img {
        max-width: 260px;
        max-height: 320px;
        border-radius: 10px;
        box-shadow: 0 1px 8px rgba(0,0,0,0.10);
        display: block;
      }
      @media (max-width: 640px) {
        .chat-container { border-radius: 0; margin: 0; box-shadow: none; }
        .chat-header, .chat-messages { padding: 0 10px; }
        .chat-messages { gap: 16px; }
        .msg-content { max-width: 88vw; }
      }
    </style>
  `

  // 判断自己和他人（导出记录时可能没有当前用户信息，这里全部用“user”或“other”交错美化）
  let lastSenderId = null

  // 渲染消息
  const messageHtml = messages.map(msg => {
    const isUser = msg.senderId === undefined
      ? false
      : (!lastSenderId || msg.senderId === lastSenderId)
        ? false
        : true // 简单交错
    lastSenderId = msg.senderId

    // 头像首字母
    const avatar = msg.senderName?.[0] || "U"
    // 时间
    const timeStr = msg.time
      ? new Date(msg.time).toLocaleString()
      : (msg.send_time ? new Date(msg.send_time).toLocaleString() : '')
    // 名字
    const senderName = msg.senderName || msg.sender_name || '未知'
    // 气泡内容
    let bubble
    if (msg.type === 'image' || msg.msg_type === 'image') {
      if (msg.content && msg.content.startsWith('data:image')) {
        bubble = `<span class="msg-bubble"><img src="${msg.content}" alt="图片" /></span>`
      } else {
        bubble = `<span class="msg-bubble" style="color:#888;font-style:italic;">[图片丢失]</span>`
      }
    } else {
      bubble = `<span class="msg-bubble">${escapeHtml(msg.content || msg.text)}</span>`
    }

    // 判断是否右侧气泡
    const isRight = msg.senderId === undefined
      ? false
      : props && props.currentUser && msg.senderId === props.currentUser.id

    return `
      <div class="msg-row${isRight ? ' user' : ''}">
        <div class="msg-avatar">${avatar}</div>
        <div class="msg-content">
          <div class="msg-meta">
            <span class="name">${escapeHtml(senderName)}</span>
            <span class="time">${timeStr}</span>
          </div>
          ${bubble}
        </div>
      </div>
    `
  }).join('\n')

  return `
  <!DOCTYPE html>
  <html lang="zh">
  <head>
    <meta charset="UTF-8" />
    <title>聊天记录导出</title>
    ${style}
  </head>
  <body>
    <div class="chat-root">
      <div class="chat-container">
        <div class="chat-header">
          <h2>聊天记录导出</h2>
          <div class="type">${chatType === 'group' ? '群聊' : '单聊'} · 导出时间：${new Date().toLocaleString()}</div>
        </div>
        <div class="chat-messages">
          ${messageHtml}
        </div>
      </div>
    </div>
  </body>
  </html>
  `
}

// 转义函数
function escapeHtml(text) {
  if (!text) return ''
  return text.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
}

// 触发浏览器下载html文件
function downloadHtmlFile(content, filename) {
  const blob = new Blob([content], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
// 导出函数
function exportMessage(msg) {
  downloadMessageAsHTML(msg)
}

// 连接 socket
onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (user) {
    socket.connect(user.id)
    username.value = user.username
  }
  socket.onSingleMessage(handleSingleMessage)
  socket.onGroupMessage(handleGroupMessage)
  socket.onGroupImage(handleGroupImage)
  socket.onSingleImage(handleSingleImage)

})
onUnmounted(() => {
  socket.offSingleMessage(handleSingleMessage)
  socket.offGroupMessage(handleGroupMessage)
  socket.offGroupImage(handleGroupImage)
})

// 收到单聊消息
const emit = defineEmits(['group-dissolved', 'new-message'])
function handleSingleMessage(msg) {
  // 判断是否为当前窗口相关消息
  const isCurrent = props.chat && (
    (msg.from === props.currentUser.id && msg.to === props.chat.id) ||
    (msg.from === props.chat.id && msg.to === props.currentUser.id)
  )
  if (isCurrent) {
    messages.value.push({
      id: msg.id || Date.now(),
      senderId: msg.from,
      senderName: props.currentUser.username || '',
      type: msg.msg_type,
      content: msg.content,
      time: msg.send_time
    })
    nextTick(scrollToBottom)
  }
  // 无论是否当前窗口，都向父组件派发新消息事件，带内容
  emit('new-message', {
    chatId: msg.from === props.currentUser.id ? msg.to : msg.from,
    chatType: 'user',
    content: msg.content,
    msgType: msg.msg_type,
    senderName: ''
  })
}

// 收到单聊图片消息
async function handleSingleImage(msg) {
  if (
    props.chat &&
    (
      (msg.from === props.currentUser.id && msg.to === props.chat.id) ||
      (msg.from === props.chat.id && msg.to === props.currentUser.id)
    )
  ) {
    if (msg.filename && msg.image?.startsWith('data:image')) {
      await saveImageToDB(msg.filename, msg.image)
    }

    let imageData = null
    if (msg.filename) {
      imageData = await getImageFromDB(msg.filename)
    }

    messages.value.push({
      id: msg.id || Date.now(),
      senderId: msg.from,
      senderName: '',
      type: 'image',
      content: imageData || msg.image || '[图片丢失]',
      filename: msg.filename,
      time: msg.send_time
    })
    nextTick(scrollToBottom)
  }
}

// 删除消息
async function deleteMessage(msg) {
  if (!msg?.id) return;
  const confirmed = window.confirm('确定删除这条消息吗？');
  if (!confirmed) return;

  // 从 localStorage 取出 user 信息，解析为对象
  const userStr = localStorage.getItem('user');
  if (!userStr) {
    alert('用户未登录或未找到用户信息');
    return;
  }
  const user = JSON.parse(userStr);

  console.log("删除消息的Id:", msg.id);

  try {
    // 传 user_id 作为 query 参数
    await request.delete(`/api/message/delete/${msg.id}?user_id=${user.id}`);

    // 删除成功后，从 messages 数组里移除该条消息
    const idx = messages.value.findIndex(m => m.id === msg.id);
    if (idx !== -1) {
      messages.value.splice(idx, 1);
    }
  } catch (error) {
    alert('删除失败，请稍后重试');
  }
}


// 软删除函数，针对非自己消息只从本地移除，不调用接口
function softDeleteMessage(msg) {
  if (!msg?.id) return;
  const confirmed = window.confirm('确定从当前聊天中移除这条消息吗？');
  if (!confirmed) return;
  const idx = messages.value.findIndex(m => m.id === msg.id);
  if (idx !== -1) messages.value.splice(idx, 1);
}



// 拉历史消息
async function fetchMessages(chat) {
  loading.value = true
  let url = ''
  let params = {}
  if (chat.type === 'user') {
    url = '/api/chat/history'
    params = { user_id: props.currentUser.id, peer_id: chat.id, page: 1, page_size: 30 }
  } else if (chat.type === 'group') {
    url = '/api/chat/group_history'
    params = { group_id: chat.id, page: 1, page_size: 30 }
  } else {
    messages.value = []
    loading.value = false
    return
  }

  try {
    const resp = await request.get(url, { params })

    const rawMessages = resp.data.data.messages || []

    console.log("接收到的消息:",rawMessages)

    const resolvedMessages = await Promise.all(rawMessages.map(async (msg, idx) => {
      const base = {
        id: msg.id,
        senderId: msg.sender_id,
        senderName: msg.sender_name || '',
        type: msg.msg_type,
        content: msg.content,
        time: msg.send_time,
        avatarUrl: msg.avatar_url || ''
      }

      if (msg.msg_type === 'image' && msg.extra?.filename) {
        const imageData = await getImageFromDB(msg.extra.filename)
        return {
          ...base,
          type: 'image',
          content: imageData || '[图片已丢失]',
          filename: msg.extra.filename,
          imageId: msg.extra.image_id
        }
      }

      return base
    }))

    messages.value = resolvedMessages
    nextTick(scrollToBottom)
  } catch (e) {
    messages.value = []
  } finally {
    loading.value = false
  }

}


// 发送文字消息
const inputText = ref('')
function sendText() {
  const text = inputText.value.trim()
  if (!text || !props.chat) return

  if (props.chat.type === 'group') {
    // 群聊
    socket.sendGroupMessage({
      from: props.currentUser.id,
      group_id: props.chat.id,
      content: text,
      sender_name: props.currentUser.name || props.currentUser.nickname || props.currentUser.username
    })
  } else {
    // 单聊
    socket.sendSingleMessage({
      from: props.currentUser.id,
      to: props.chat.id,
      content: text
    })
  }

  // 本地回显
  messages.value.push({
    id: Date.now(),
    senderId: props.currentUser.id,
    senderName: props.currentUser.username || '',
    type: 'text',
    content: text,
    time: Date.now()
  })
  inputText.value = ''
  nextTick(scrollToBottom)
}

// 自动滚到底
const chatBodyRef = ref(null)
function scrollToBottom() {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}
// async function fetchMessages(chat) {
//   loading.value = true
//   let url = ''
//   let params = {}
//   if (chat.type === 'user') {
//     url = '/api/chat/history'
//     params = { user_id: props.currentUser.id, peer_id: chat.id, page: 1, page_size: 30 }
//   } else if (chat.type === 'group') {
//     url = '/api/chat/group_history'
//     params = { group_id: chat.id, page: 1, page_size: 30 }
//   }
//   try {
//     const resp = await request.get(url, { params })
//     // 字段适配
//     messages.value = resp.data.data.messages.map(msg => ({
//       id: msg.id,
//       senderId: msg.sender_id,
//       senderName: msg.sender_name,
//       type: msg.msg_type,
//       content: msg.content,
//       time: msg.send_time,
//       avatarUrl: msg.avatar_url || '', // 适配头像（可选）
//     }))
//   } catch (e) {
//     // 错误处理
//     messages.value = []
//   } finally {
//     loading.value = false
//   }
// }

// 判断是不是群聊
const isGroup = computed(() => props.chat?.type === 'group')

// // 当选择聊天对象时加载历史
// watch(() => props.chat, (chat) => {
//   if (chat) fetchMessages(chat)
// }, { immediate: true })




const showGroupManageDialog = ref(false)
function openGroupManageDialog() {
  showGroupManageDialog.value = true
}
function closeGroupManageDialog() {
  showGroupManageDialog.value = false
}

// 监听props.chat变化，只拉取历史消息（群成员管理交给弹窗组件）
watch(() => props.chat, (chat) => {
  if (chat) {
    fetchMessages(chat)
  }
}, { immediate: true })

// 已在顶部定义 emit，无需重复定义
function handleGroupDissolved() {
  // 只负责向父组件冒泡事件，不再请求接口
  emit('group-dissolved')
  showGroupManageDialog.value = false
}


// 全屏图片查看
const fullImage = ref(null)
function openImage(url) {
  fullImage.value = url
}
function closeImage() {
  fullImage.value = null
}

// // 发送消息
// const inputText = ref('')
// const inputRef = ref(null)
// function sendText() {
//   const text = inputText.value.trim()
//   if (!text) return
//   messages.value.push({
//     id: Date.now(),
//     senderId: props.currentUser.id,
//     senderName: props.currentUser.name,
//     type: 'text',
//     content: text,
//     time: Date.now()
//   })
//   inputText.value = ''
//   nextTick(() => scrollToBottom())
// }

// 发送图片
function handleImageChange(e) {
  const file = e.target.files[0]
  if (!file || !props.chat) return

  const maxSize = 1 * 1024 * 1024 // 1MB
  if (file.size > maxSize) {
    alert('图片大小不能超过 1MB')
    e.target.value = ''
    return
  }

  if (props.chat.type === 'group') {
    sendGroupImage(file)
  } else {
    const reader = new FileReader()
    reader.onload = async () => {
      const base64Data = typeof reader.result === 'string' ? reader.result : ''

      await saveImageToDB(file.name, base64Data)

      socket.sendSingleImage({
        from: props.currentUser.id,
        to: props.chat.id,
        image: base64Data,
        filename: file.name,
        extra: {}
      })

      messages.value.push({
        id: Date.now(),
        senderId: props.currentUser.id,
        senderName: props.currentUser.name || '',
        type: 'image',
        content: base64Data,
        filename: file.name,
        time: Date.now()
      })
      nextTick(scrollToBottom)
    }
    reader.readAsDataURL(file)
  }

  e.target.value = ''
}



// 输入框自适应高度
function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  const maxHeight = window.innerHeight * 0.25
  el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px'
}

// const chatBodyRef = ref(null)
// function scrollToBottom() {
//   if (chatBodyRef.value) {
//     chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
//   }
// }

function handleGroupMessage(msg) {
  const isCurrent = isGroup.value && msg.group_id === props.chat.id
  if (isCurrent) {
    messages.value.push({
      id: msg.id || Date.now(),
      senderId: msg.sender_id,
      senderName: msg.sender_name || '',
      type: msg.msg_type,
      content: msg.content,
      time: msg.send_time
    })
    nextTick(scrollToBottom)
  }
  // 派发新群聊消息事件，带内容
  emit('new-message', {
    chatId: msg.group_id,
    chatType: 'group',
    content: msg.content,
    msgType: msg.msg_type,
    senderName: msg.sender_name || ''
  })
}
async function handleGroupImage(msg) {
  if (
    isGroup.value &&
    msg.group_id === props.chat.id
  ) {
    if (msg.filename && msg.image?.startsWith('data:image')) {
      await saveImageToDB(msg.filename, msg.image)
    }

    messages.value.push({
      id: msg.id || Date.now(),
      senderId: msg.sender_id,
      senderName: msg.sender_name || '',
      type: 'image',
      content: msg.image,
      filename: msg.filename,
      imageId: msg.image_id,
      time: msg.send_time
    })
    nextTick(scrollToBottom)
  }
}

// // 发送消息
// function sendGroupText() {
//   const text = inputText.value.trim()
//   if (!text || !props.chat) return
//   socket.sendGroupMessage({
//     from: props.currentUser.id,
//     group_id: props.chat.id,
//     content: text,
//     sender_name: props.currentUser.name || props.currentUser.nickname || props.currentUser.username
//   })
//   // 本地回显
//   messages.value.push({
//     id: Date.now(),
//     senderId: props.currentUser.id,
//     type: 'text',
//     content: text,
//     time: Date.now()
//   })
//   inputText.value = ''
//   nextTick(scrollToBottom)
// }

// 发送图片
function sendGroupImage(file) {
  const reader = new FileReader()
  reader.onload = async function () {
    const base64Data = typeof reader.result === 'string' ? reader.result : ''
    await saveImageToDB(file.name, base64Data)
    socket.sendGroupImage({
      from: props.currentUser.id,
      group_id: props.chat.id,
      image: reader.result,
      filename: file.name,
      extra: {}, // 可选图片尺寸
      sender_name: props.currentUser.name || props.currentUser.nickname || props.currentUser.username
    })
    messages.value.push({
      id: Date.now(),
      senderId: props.currentUser.id,
      type: 'image',
      content: reader.result,
      filename: file.name,
      senderName: props.currentUser.name || '',
      time: Date.now()
    })
  }
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="flex flex-col h-full w-full bg-gray-50">

    <!-- Header -->
    <div class="flex items-center px-4 h-16 border-b border-gray-200 bg-white/80">
      <template v-if="isGroup">
      <div class="flex items-center flex-1 min-w-0">
        <span class="text-lg font-bold text-gray-800 truncate">
          {{ props.chat?.name }}
        </span>
      </div>
      <button
        class="ml-4 flex items-center px-3 py-1.5 rounded-lg border border-gray-300 text-gray-700 hover:border-blue-400 hover:text-blue-600 transition-all duration-150 bg-transparent font-medium"
        @click="openGroupManageDialog"
      >
        <UIcon name="material-symbols:group" class="size-5 mr-2" />
        群管理
      </button>
      <button
        class="ml-2 flex items-center px-3 py-1.5 rounded-lg border border-gray-300 text-gray-700 hover:border-blue-400 hover:text-blue-600 transition-all duration-150 bg-transparent font-medium"
        @click="exportChatHistory"
      >
        <UIcon name="material-symbols:file-export-rounded" class="size-5 mr-2" />
        导出记录
      </button>
    </template>

    <template v-else>
      <div class="flex items-center flex-1 min-w-0">
        <span class="text-lg font-bold text-gray-800 truncate">{{ props.chat?.name }}</span>
      </div>
      <button
        class="ml-4 flex items-center px-3 py-1.5 rounded-lg border border-gray-300 text-gray-700 hover:border-blue-400 hover:text-blue-600 transition-all duration-150 bg-transparent font-medium"
        @click="exportChatHistory"
      >
        <UIcon name="material-symbols:file-export-rounded" class="size-5 mr-2" />
        导出记录
      </button>
    </template>
    </div>


    <!-- 群管理弹窗 -->
    <GroupManageDialog
      :show="showGroupManageDialog"
      :chat="props.chat"
      @close="closeGroupManageDialog"
      @group-dissolved="handleGroupDissolved"
      @member-changed="() => {}"
    />

    <!-- 添加成员弹窗 -->
    <div v-if="showAddUserDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-md p-6 relative">
        <h2 class="text-lg font-bold mb-4">选择要添加的成员</h2>
        <ul class="mb-4 max-h-60 overflow-y-auto">
          <li v-for="u in addableUsers" :key="u.id" class="flex items-center justify-between py-2 border-b last:border-b-0">
            <span>{{ u.name }}</span>
            <button class="text-blue-500 hover:underline text-sm" @click="addGroupMember(u.id)">添加</button>
          </li>
        </ul>
        <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-700" @click="closeAddUserDialog">
          <IconClose class="w-6 h-6" />
        </button>
      </div>
    </div>

    <!-- 聊天消息区 -->
    <div ref="chatBodyRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-10">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="relative flex"
        :class="msg.senderId === props.currentUser.id ? 'justify-end' : 'justify-start'"
      >
        <!-- 消息块 -->
        <div class="relative group max-w-[75%] flex items-end">

          <!-- 左侧头像 -->
          <div
            v-if="isGroup && msg.senderId !== props.currentUser.id"
            class="mr-2 w-8 h-8 flex-shrink-0 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-base"
          >
            {{ msg.senderName[0] }}
          </div>

          <!-- 消息气泡 -->
          <div
            :class="[
              'relative px-4 py-2 rounded-2xl break-words',
              msg.senderId === props.currentUser.id
                ? 'bg-blue-500 text-white rounded-br-md'
                : 'bg-gray-200 text-black rounded-bl-md'
            ]"
            class="w-fit max-w-full"
          >
            <template v-if="msg.type === 'text'">
              <span class="whitespace-pre-line break-words leading-relaxed">
                {{ msg.content }}
              </span>
            </template>

            <template v-else-if="msg.type === 'image'">
              <img
                :src="msg.content"
                class="w-40 max-w-xs rounded-xl cursor-pointer transition hover:scale-105"
                @click="openImage(msg.content)"
                alt="图片丢失"
              />
            </template>

            <!-- 操作按钮 -->
            <div class="absolute -bottom-8 right-0 flex space-x-1">
              <button
                @click.stop="exportMessage(msg)"
                class="w-6 h-6 flex items-center justify-center rounded-full text-gray-400 hover:bg-white hover:text-blue-600 transition"
                title="导出为 HTML"
              >
                <IconDownload class="w-4 h-4" />
              </button>
              <button
                @click.stop="msg.senderId === props.currentUser.id ? deleteMessage(msg) : softDeleteMessage(msg)"
                class="w-6 h-6 flex items-center justify-center rounded-full text-gray-400 hover:bg-white hover:text-red-500 transition"
                title="删除消息"
              >
                <IconDelete class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- 右侧头像（自己） -->
          <div
            v-if="isGroup && msg.senderId === props.currentUser.id"
            class="ml-2 w-8 h-8 flex-shrink-0 rounded-full bg-blue-200 text-blue-700 flex items-center justify-center font-bold text-base"
          >
            {{ msg.senderName && msg.senderName.length > 0 ? msg.senderName[0] : '你' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 图片放大查看 -->
    <div
      v-if="fullImage"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 pointer-events-auto"
    >
      <img
        :src="fullImage"
        class="max-h-[80vh] max-w-[90vw] rounded-xl object-contain"
      />
      <button
        class="absolute top-6 right-10 bg-white/90 rounded-full p-2 shadow text-gray-800 hover:bg-blue-100 transition"
        @click="closeImage"
      >
        <IconClose class="w-6 h-6" />
      </button>
    </div>

    <!-- 输入框 -->
    <div class="flex items-end px-4 py-3 bg-white border-t border-gray-200">
      <textarea
        ref="inputRef"
        v-model="inputText"
        @input="autoResize"
        rows="1"
        placeholder="请输入消息…"
        class="flex-1 resize-none p-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-gray-50 text-base max-h-[25vh] overflow-auto"
        style="line-height:1.5;"
      ></textarea>
      <input
        type="file"
        accept="image/*"
        class="hidden"
        id="chat-image-upload"
        @change="handleImageChange"
      />
      <label for="chat-image-upload" class="ml-2 cursor-pointer p-2 rounded hover:bg-blue-50">
        <IconImage class="w-6 h-6 text-blue-500" />
      </label>
      <button
        :disabled="!inputText.trim()"
        @click="sendText"
        class="ml-2 p-2 rounded transition text-white"
        :class="inputText.trim()
          ? 'bg-blue-400 hover:bg-blue-500'
          : 'bg-blue-200 cursor-not-allowed'"
      >
        <IconSend class="w-6 h-6" />
      </button>
    </div>
  </div>
</template>


