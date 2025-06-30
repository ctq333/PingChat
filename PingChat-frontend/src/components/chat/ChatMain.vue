<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import request from '@/utils/request'
import socket from '@/utils/socket'
import { saveImageToDB, getImageFromDB } from '@/utils/userChatStorage'


import IconSend from '~icons/material-symbols/send'
import IconImage from '~icons/material-symbols/image'
import IconClose from '~icons/material-symbols/close'

const props = defineProps({
  chat: Object,
  currentUser: {
    type: Object,
  }
})

const messages = ref([])
const loading = ref(false)

// 连接 socket
onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (user) socket.connect(user.id)
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
function handleSingleMessage(msg) {
  // 只显示发给自己或自己发出的且和当前窗口相关的消息
  if (
    props.chat &&
    (
      (msg.from === props.currentUser.id && msg.to === props.chat.id) ||
      (msg.from === props.chat.id && msg.to === props.currentUser.id)
    )
  ) {
    messages.value.push({
      id: msg.id || Date.now(),
      senderId: msg.from,
      senderName: '', // 可选补充
      type: msg.msg_type,
      content: msg.content,
      time: msg.send_time
    })
    nextTick(scrollToBottom)
  }
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
    // 👇 如果收到图片 base64 且带 filename，则保存到本地
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

    // 异步组装带图片内容的消息
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


// 监听切换聊天对象时拉历史
watch(() => props.chat, (chat) => {
  if (chat) fetchMessages(chat)
}, { immediate: true })

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
      content: text
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



// 群成员管理弹窗控制
const showGroupManageDialog = ref(false)
// function openGroupManageDialog() {  // <-- 删除多余的声明
//   showGroupManageDialog.value = true
// }

function closeGroupManageDialog() {
  showGroupManageDialog.value = false
}

// 群成员列表
const groupMembers = ref([])
// 可添加的用户列表
const addableUsers = ref([])
const showAddUserDialog = ref(false)

// 查询群成员
async function fetchGroupMembers(chatId) {
  const gid = chatId || props.chat?.id
  if (!gid) return
  // 需要后端接口：GET /api/group/members?group_id=xxx
  // 返回格式建议：[{id, name}]
  const resp = await request.get('/api/group/members', { params: { group_id: gid } })
  groupMembers.value = resp.data.data || []
}

// 查询可添加用户
async function fetchAddableUsers() {
  if (!props.chat?.id) return
  // 需要后端接口：GET /api/group/addable_users?group_id=xxx
  // 返回格式建议：[{id, name}]
  const resp = await request.get('/api/group/addable_users', { params: { group_id: props.chat.id } })
  addableUsers.value = resp.data.data || []
}

// function openGroupManageDialog() {
//   showGroupManageDialog.value = true
//   fetchGroupMembers()
// }
// function closeGroupManageDialog() {
//   showGroupManageDialog.value = false
// }

// 打开添加成员弹窗
async function openAddUserDialog() {
  await fetchAddableUsers()
  showAddUserDialog.value = true
}
function closeAddUserDialog() {
  showAddUserDialog.value = false
}

// 添加成员（本地先移除，接口成功后再刷新，提升体验）
async function addGroupMember(userId) {
  // 本地先移除，提升响应
  addableUsers.value = addableUsers.value.filter(u => u.id !== userId)
  await request.post('/api/group/add_member', {
    group_id: props.chat.id,
    user_id: userId
  })
  // 只刷新群成员列表，不立即关闭弹窗
  fetchGroupMembers()
}

// 删除成员（本地先移除，接口成功后再刷新，提升体验）
async function removeGroupMember(userId) {
  groupMembers.value = groupMembers.value.filter(m => m.id !== userId)
  await request.post('/api/group/remove_member', {
    group_id: props.chat.id,
    user_id: userId
  })
  // 删除后可选刷新addableUsers，避免下次切换tab时数据不一致
}


// tab切换时立即加载数据，避免切换卡顿
function switchManageTab(tab) {
  manageTab.value = tab
  if (tab === 'remove') {
    // 只在切换到删除tab时刷新群成员
    fetchGroupMembers()
  } else {
    // 只在切换到添加tab时刷新可添加用户
    fetchAddableUsers()
  }
}


// 群管理弹窗tab
const manageTab = ref('remove')

// 打开管理弹窗时刷新群成员并默认选中删除成员tab
function openGroupManageDialog() {
  showGroupManageDialog.value = true
  manageTab.value = 'remove'
  fetchGroupMembers()
}

// 监听props.chat变化，拉取历史消息，并若为群聊则自动拉取群成员（用于显示人数）
watch(() => props.chat, (chat) => {
  if (chat) {
    fetchMessages(chat)
    if (chat.type === 'group') {
      fetchGroupMembers(chat.id)
    }
  }
}, { immediate: true })

// 解散群聊弹窗控制
const showDissolveDialog = ref(false)
function openDissolveDialog() {
  showDissolveDialog.value = true
}
function closeDissolveDialog() {
  showDissolveDialog.value = false
}
// 解散群聊
const emit = defineEmits(['group-dissolved'])
async function dissolveGroup() {
  if (!props.chat?.id) return
  // 立即关闭弹窗，提升体验
  showDissolveDialog.value = false
  showGroupManageDialog.value = false
  // 先请求后端，成功后再通知父组件（确保 ChatView 的 handleGroupDissolved 只在后端成功时调用）
  try {
    await request.post('/api/group/dissolve', { group_id: props.chat.id })
    emit('group-dissolved')
  } catch (e) {
    // 可选：全局错误提示
  }
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

  // 👉 判断图片大小（1MB = 1024 * 1024）
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
  if (
    isGroup.value &&
    msg.group_id === props.chat.id
  ) {
    messages.value.push({
      id: msg.id || Date.now(),
      senderId: msg.sender_id,
      senderName: msg.sender_name || '', // 这里要保证 senderName 有值
      type: msg.msg_type,
      content: msg.content,
      time: msg.send_time
    })
    nextTick(scrollToBottom)
  }
}
async function handleGroupImage(msg) {
  if (
    isGroup.value &&
    msg.group_id === props.chat.id
  ) {
    // 👇 尝试保存图片到接收方本地 IndexedDB（防止刷新后丢失）
    if (msg.filename && msg.image?.startsWith('data:image')) {
      await saveImageToDB(msg.filename, msg.image)
    }

    // 👇 渲染消息（图片内容来自 socket 传来的 base64）
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

// 发送消息
function sendGroupText() {
  const text = inputText.value.trim()
  if (!text || !props.chat) return
  socket.sendGroupMessage({
    from: props.currentUser.id,
    group_id: props.chat.id,
    content: text
  })
  // 本地回显
  messages.value.push({
    id: Date.now(),
    senderId: props.currentUser.id,
    type: 'text',
    content: text,
    time: Date.now()
  })
  inputText.value = ''
  nextTick(scrollToBottom)
}

// 发送图片
function sendGroupImage(file) {
  const reader = new FileReader()
  reader.onload = function () {
    socket.sendGroupImage({
      from: props.currentUser.id,
      group_id: props.chat.id,
      image: reader.result,
      filename: file.name,
      extra: {} // 可选图片尺寸
    })
    messages.value.push({
      id: Date.now(),
      senderId: props.currentUser.id,
      type: 'image',
      content: reader.result,
      filename: file.name,
      time: Date.now()
    })
  }
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="flex flex-col h-full w-full bg-gray-50">
    <!-- header -->
    <div class="flex items-center px-4 h-16 border-b border-gray-200 bg-white/80">
      <template v-if="isGroup">
        <div class="flex items-center flex-1 min-w-0">
          <span class="text-lg font-bold text-gray-800 truncate">
            {{ props.chat?.name }}
            <span class="ml-1 text-sm font-normal text-gray-500">({{ groupMembers.length }})</span>
          </span>
        </div>
        <button
          class="ml-4 flex items-center px-3 py-1.5 rounded-lg bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white text-sm font-semibold shadow transition-all duration-150"
          @click="openGroupManageDialog"
        >
          <Icon name="material-symbols:manage-accounts" class="w-5 h-5 mr-2" />群管理
        </button>
      </template>
      <template v-else>
        <span class="text-lg font-bold text-gray-800 truncate">{{ props.chat?.name }}</span>
      </template>
    </div>

    <!-- 群成员管理弹窗 -->
    <div v-if="showGroupManageDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-md p-6 relative">
        <h2 class="text-lg font-bold mb-4">群成员管理</h2>
        <div class="flex items-center mb-4">
          <button
            class="flex-1 py-2 rounded-l-lg text-sm font-semibold transition-all duration-150"
            :class="manageTab === 'remove' ? 'bg-blue-500 text-white shadow' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            @click="switchManageTab('remove')"
          >
            删除成员
          </button>
          <button
            class="flex-1 py-2 rounded-r-lg text-sm font-semibold transition-all duration-150"
            :class="manageTab === 'add' ? 'bg-blue-500 text-white shadow' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            @click="switchManageTab('add')"
          >
            添加成员
          </button>
        </div>
        <div v-if="manageTab === 'remove'">
          <ul class="mb-4 max-h-60 overflow-y-auto">
            <li v-for="m in groupMembers" :key="m.id" class="flex items-center justify-between py-2 border-b last:border-b-0">
              <span>{{ m.name }}</span>
              <button class="text-red-500 hover:underline text-sm" @click="removeGroupMember(m.id)">移除</button>
            </li>
          </ul>
        </div>
        <div v-else>
          <ul class="mb-4 max-h-60 overflow-y-auto">
            <li v-for="u in addableUsers" :key="u.id" class="flex items-center justify-between py-2 border-b last:border-b-0">
              <span>{{ u.name }}</span>
              <button class="text-blue-500 hover:underline text-sm" @click="addGroupMember(u.id)">添加</button>
            </li>
          </ul>
        </div>

        <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-700" @click="closeGroupManageDialog">
          <IconClose class="w-6 h-6" />
        </button>
        <!-- 解散群聊按钮 -->
        <button
          class="w-full mt-2 py-2 rounded bg-red-500 hover:bg-red-600 text-white font-semibold transition"
          @click="openDissolveDialog"
        >
          解散群聊
        </button>

        <!-- 解散群聊确认弹窗 -->
        <div v-if="showDissolveDialog" class="fixed inset-0 z-60 flex items-center justify-center bg-black/40">
          <div class="bg-white rounded-lg shadow-lg w-full max-w-xs p-6 relative flex flex-col items-center">
            <h3 class="text-lg font-bold mb-2 text-center">解散群聊</h3>
            <p class="text-gray-700 text-sm mb-6 text-center">确定要解散该群聊吗？此操作不可恢复！</p>
            <div class="flex w-full space-x-3">
              <button class="flex-1 py-2 rounded bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold" @click="closeDissolveDialog">取消</button>
              <button class="flex-1 py-2 rounded bg-red-500 hover:bg-red-600 text-white font-semibold" @click="dissolveGroup">确定</button>
            </div>
          </div>
        </div>
      </div>
    </div>


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
    <div ref="chatBodyRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-2">
      <div v-for="msg in messages" :key="msg.id" class="flex"
        :class="msg.senderId === props.currentUser.id ? 'justify-end' : 'justify-start'">
        <!-- 头像（群聊时显示别人，自己不用） -->
        <div v-if="isGroup && msg.senderId !== props.currentUser.id" class="mr-2 flex-shrink-0">
          <div
            class="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-base">
            {{ msg.senderName[0] }}
          </div>
        </div>
        <!-- 气泡 -->
        <div :class="[
          'max-w-[65%] min-w-[48px] px-3 py-2 rounded-2xl relative',
          msg.senderId === props.currentUser.id
            ? 'bg-blue-400 text-white rounded-br-md'
            : 'bg-gray-200 text-black rounded-bl-md'
        ]">
          <!-- 文字消息 -->
          <template v-if="msg.type === 'text'">
            <span class="whitespace-pre-line break-words leading-relaxed">{{ msg.content }}</span>
          </template>
          <!-- 图片消息 -->
          <template v-else-if="msg.type === 'image'">
            <img :src="msg.content" class="w-40 max-w-xs rounded-xl cursor-pointer transition hover:scale-105"
              @click="openImage(msg.content)" alt="图片丢失" />
          </template>
        </div>
        <!-- 头像（自己发的显示在右侧/群聊） -->
        <div v-if="isGroup && msg.senderId === props.currentUser.id" class="ml-2 flex-shrink-0">
          <div
            class="w-8 h-8 rounded-full bg-blue-200 text-blue-700 flex items-center justify-center font-bold text-base">
            {{ (msg.senderName && msg.senderName.length > 0) ? msg.senderName[0] : '' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 全屏图片查看 -->
    <div v-if="fullImage" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <img :src="fullImage" class="max-h-[80vh] max-w-[90vw] rounded-xl object-contain" />
      <button
        class="absolute top-6 right-10 bg-white/90 rounded-full p-2 shadow text-gray-800 hover:bg-blue-100 transition"
        @click="closeImage">
        <IconClose class="w-6 h-6" />
      </button>
    </div>

    <!-- footer 输入区 -->
    <div class="flex items-end px-4 py-3 bg-white border-t border-gray-200">
      <textarea ref="inputRef" v-model="inputText" @input="autoResize" rows="1" placeholder="请输入消息…"
        class="flex-1 resize-none p-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-gray-50 text-base max-h-[25vh] overflow-auto"
        style="line-height:1.5;"></textarea>
      <input type="file" accept="image/*" class="hidden" id="chat-image-upload" @change="handleImageChange" />
      <label for="chat-image-upload" class="ml-2 cursor-pointer p-2 rounded hover:bg-blue-50">
        <IconImage class="w-6 h-6 text-blue-500" />
      </label>
      <button :disabled="!inputText.trim()" @click="sendText" class="ml-2 p-2 rounded transition text-white" :class="inputText.trim()
        ? 'bg-blue-400 hover:bg-blue-500'
        : 'bg-blue-200 cursor-not-allowed'">
        <IconSend class="w-6 h-6" />
      </button>
    </div>
  </div>
</template>