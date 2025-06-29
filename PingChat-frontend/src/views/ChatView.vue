<script setup>
import { ref, onMounted } from 'vue'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatMain from '@/components/chat/ChatMain.vue'
import request from '@/utils/request' // 你的 axios 工具

const currentUser = ref({ id: 1, name: '我' })

// 会话/联系人/群组列表
const chatList = ref([])

// 当前激活会话
const activeChat = ref(null)

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
    chatList.value = resp.data.data.map(item => ({
      id: item.id,
      name: item.name,
      type: item.type, // "user" 或 "group"
      lastMsgTime: item.last_msg_time,
      lastMsg: item.last_msg,
      avatarUrl: item.avatar_url // 可选
    }))
  } catch (e) {
    chatList.value = []
  }
}

// 选中会话
function handleSelectChat(chat) {
  activeChat.value = chat
}

onMounted(fetchChatList)
</script>

<template>
  <div class="flex w-screen h-screen bg-gray-50">
    <ChatSidebar
      :chatList="chatList"
      :currentUser="currentUser"
      :activeChat="activeChat"
      @select-chat="handleSelectChat"
    />
    <div class="flex-1 flex flex-col">
      <ChatMain
        v-if="activeChat"
        :chat="activeChat"
        :currentUser="currentUser"
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