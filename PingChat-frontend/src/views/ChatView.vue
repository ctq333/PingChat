<script setup>
import { ref, onMounted } from 'vue'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatMain from '@/components/chat/ChatMain.vue'
import request from '@/utils/request' // 你的 axios 工具

const currentUser = ref(null)

// 会话/联系人/群组列表
const chatList = ref([])

// 当前激活会话
const activeChat = ref(null)
// 未读消息计数，key: `${id}-${type}`
const unreadMap = ref({})

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (user) currentUser.value = user
})
// 拉取会话列表
async function fetchChatList() {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const userId = user ? user.id : null
  if (!userId) return
  try {
    const resp = await request.get('/api/chat/session_list', {
      params: { user_id: userId }
    })
    // 字段适配
    const newList = resp.data.data.map(item => ({
      id: item.id,
      name: item.name,
      type: item.type, // "user" 或 "group"
      lastMsgTime: item.last_msg_time,
      lastMsg: item.last_msg,
      avatarUrl: item.avatar_url // 可选
    }))
    chatList.value = newList
    // 如果当前激活会话已不存在于新列表，则自动清空
    if (activeChat.value && !newList.some(c => c.id === activeChat.value.id && c.type === activeChat.value.type)) {
      activeChat.value = null
    }
  } catch (e) {
    chatList.value = []
    activeChat.value = null
  }
}

// 选中会话
function handleSelectChat(chat) {
  activeChat.value = chat
  // 清除该会话的未读数
  if (chat) {
    const key = `${chat.id}-${chat.type}`
    if (unreadMap.value[key]) unreadMap.value[key] = 0
  }
}

// 处理新消息事件，更新未读数
function handleNewMessage({ chatId, chatType }) {
  // 如果不是当前激活会话，未读数+1
  if (!activeChat.value || activeChat.value.id !== chatId || activeChat.value.type !== chatType) {
    const key = `${chatId}-${chatType}`
    unreadMap.value[key] = (unreadMap.value[key] || 0) + 1
  }
}

onMounted(fetchChatList)
function handleGroupCreated() {
  fetchChatList()  // 刷新列表，显示新群组
}
function handleGroupDissolved() {
  activeChat.value = null
  fetchChatList()  // 重新拉取会话列表
}
</script>

<template>
  <div class="flex w-screen h-screen bg-gray-50">
    <ChatSidebar
      :key="chatList.length"
      :chatList="chatList"
      :currentUser="currentUser"
      :activeChat="activeChat"
      :unreadMap="unreadMap"
      @select-chat="handleSelectChat"
      @group-created="fetchChatList"  
    />
    <div class="flex-1 flex flex-col">
      <ChatMain
        v-if="activeChat"
        :chat="activeChat"
        :currentUser="currentUser"
        @group-dissolved="handleGroupDissolved"
        @new-message="handleNewMessage"
      />
      <div
        v-else
        class="flex flex-1 items-center justify-center text-gray-400 text-lg"
      >
        请选择一个联系人或群组开始聊天
      </div>
    </div>
  </div>
</template>