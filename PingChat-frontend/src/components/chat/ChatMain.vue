<script setup>
import { ref, computed, nextTick } from 'vue'
import IconSend from '~icons/material-symbols/send'
import IconImage from '~icons/material-symbols/image'
import IconClose from '~icons/material-symbols/close'

// props: chat（群组或单聊对象），currentUser
const props = defineProps({
  chat: Object,
  currentUser: {
    type: Object,
    default: () => ({ id: 1, name: '我' })
  }
})

// mock 消息数据
const messages = ref([
  // { id, senderId, senderName, type: 'text'|'image', content, time }
  { id: 1, senderId: 2, senderName: '张三', type: 'text', content: '你好！', time: Date.now() - 60000 },
  { id: 2, senderId: 1, senderName: '我', type: 'text', content: '你好！很高兴见到你。', time: Date.now() - 55000 },
  { id: 3, senderId: 2, senderName: '张三', type: 'image', content: 'https://via.placeholder.com/150', time: Date.now() - 54000 },
])

// 判断是不是群聊
const isGroup = computed(() => props.chat?.type === 'group')

// 群聊成员 mock（后续可用实际接口）
const groupMembers = ref([
  { id: 2, name: '张三' },
  { id: 3, name: '李四' },
  { id: 1, name: '我' }
])

// 全屏图片查看
const fullImage = ref(null)
function openImage(url) {
  fullImage.value = url
}
function closeImage() {
  fullImage.value = null
}

// 发送消息
const inputText = ref('')
const inputRef = ref(null)
function sendText() {
  const text = inputText.value.trim()
  if (!text) return
  messages.value.push({
    id: Date.now(),
    senderId: props.currentUser.id,
    senderName: props.currentUser.name,
    type: 'text',
    content: text,
    time: Date.now()
  })
  inputText.value = ''
  nextTick(() => scrollToBottom())
}

// 发送图片
function handleImageChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const url = URL.createObjectURL(file)
  messages.value.push({
    id: Date.now(),
    senderId: props.currentUser.id,
    senderName: props.currentUser.name,
    type: 'image',
    content: url,
    time: Date.now()
  })
  nextTick(() => scrollToBottom())
  e.target.value = '' // 允许重复选择同一图片
}

// 输入框自适应高度
function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  const maxHeight = window.innerHeight * 0.25
  el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px'
}

const chatBodyRef = ref(null)
function scrollToBottom() {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}
</script>

<template>
  <div class="flex flex-col h-full w-full bg-gray-50">
    <!-- header -->
    <div class="flex items-center px-4 h-16 border-b border-gray-200 bg-white/80">
      <div v-if="isGroup" class="flex items-center space-x-2">
        <div v-for="m in groupMembers" :key="m.id" class="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-lg font-bold">
          {{ m.name[0] }}
        </div>
      </div>
      <div v-else class="text-lg font-bold text-gray-800">
        {{ props.chat?.name }}
      </div>
      <div class="ml-3 text-gray-500 text-base font-normal">{{ props.chat?.name }}</div>
    </div>

    <!-- 聊天消息区 -->
    <div ref="chatBodyRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-2">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="flex"
        :class="msg.senderId === props.currentUser.id ? 'justify-end' : 'justify-start'"
      >
        <!-- 头像（群聊时显示别人，自己不用） -->
        <div v-if="isGroup && msg.senderId !== props.currentUser.id" class="mr-2 flex-shrink-0">
          <div class="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-base">
            {{ msg.senderName[0] }}
          </div>
        </div>
        <!-- 气泡 -->
        <div
          :class="[
            'max-w-[65%] min-w-[48px] px-3 py-2 rounded-2xl relative',
            msg.senderId === props.currentUser.id
              ? 'bg-blue-400 text-white rounded-br-md'
              : 'bg-gray-200 text-black rounded-bl-md'
          ]"
        >
          <!-- 文字消息 -->
          <template v-if="msg.type === 'text'">
            <span class="whitespace-pre-line break-words leading-relaxed">{{ msg.content }}</span>
          </template>
          <!-- 图片消息 -->
          <template v-else-if="msg.type === 'image'">
            <img
              :src="msg.content"
              class="w-40 max-w-xs rounded-xl cursor-pointer transition hover:scale-105"
              @click="openImage(msg.content)"
              alt="图片消息"
            />
          </template>
        </div>
        <!-- 头像（自己发的显示在右侧/群聊） -->
        <div v-if="isGroup && msg.senderId === props.currentUser.id" class="ml-2 flex-shrink-0">
          <div class="w-8 h-8 rounded-full bg-blue-200 text-blue-700 flex items-center justify-center font-bold text-base">
            {{ msg.senderName[0] }}
          </div>
        </div>
      </div>
    </div>

    <!-- 全屏图片查看 -->
    <div v-if="fullImage" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <img :src="fullImage" class="max-h-[80vh] max-w-[90vw] rounded-xl object-contain" />
      <button
        class="absolute top-6 right-10 bg-white/90 rounded-full p-2 shadow text-gray-800 hover:bg-blue-100 transition"
        @click="closeImage"
      >
        <IconClose class="w-6 h-6" />
      </button>
    </div>

    <!-- footer 输入区 -->
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