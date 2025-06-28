<script setup>
import { ref } from 'vue'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import ChatMain from '@/components/chat/ChatMain.vue'

// 模拟当前用户
const currentUser = ref({ id: 1, name: '我' })

// 左侧联系人和群组 mock 数据
const chatList = ref([
  {
    id: 2,
    name: 'Alice',
    type: 'user',
    lastMsgTime: Date.now() - 1000 * 60 * 3,
    lastMsg: '明天见！'
  },
  {
    id: 3,
    name: 'Bob',
    type: 'user',
    lastMsgTime: Date.now() - 1000 * 60 * 60,
    lastMsg: '收到，谢谢！'
  },
  {
    id: 4,
    name: '研发群',
    type: 'group',
    lastMsgTime: Date.now() - 1000 * 60 * 10,
    lastMsg: '下周一开会'
  },
  {
    id: 5,
    name: '产品群',
    type: 'group',
    lastMsgTime: Date.now() - 1000 * 60 * 120,
    lastMsg: '上线准备'
  },
  {
    id: 6,
    name: 'Charlie',
    type: 'user',
    lastMsgTime: null, // 没有聊天记录
    lastMsg: null
  },
  {
    id: 7,
    name: '张三',
    type: 'user',
    lastMsgTime: null,
    lastMsg: null
  }
])

// 当前激活会话
const activeChat = ref(null)

// 切换会话
function handleSelectChat(chat) {
  activeChat.value = chat
}
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
      <ChatMain v-if="activeChat" :chat="activeChat" :currentUser="currentUser" />
      <div v-else class="flex flex-1 items-center justify-center text-gray-400 text-lg">
        请选择一个联系人或群组开始聊天
      </div>
    </div>
  </div>
</template>