<template>
  <div class="p-6">
    <!-- 页面头部 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center">
        <span class="material-symbols-rounded text-3xl text-green-500 mr-2">monitor_heart</span>
        <h2 class="text-2xl font-bold">聊天记录监控</h2>
      </div>
      <button class="bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2" @click="goBack">
        <span class="material-symbols-rounded"></span> 返回用户管理
      </button>
    </div>

    <!-- 筛选条件 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户ID</label>
          <input v-model="filters.userId" type="number" placeholder="输入用户ID" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">群组ID</label>
          <input v-model="filters.groupId" type="number" placeholder="输入群组ID" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">关键词</label>
          <input v-model="filters.keyword" type="text" placeholder="搜索消息内容" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">时间范围</label>
          <select v-model="filters.timeRange" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">全部时间</option>
            <option value="1h">最近1小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
          </select>
        </div>
      </div>
      <div class="flex gap-2 mt-4">
        <button class="bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2" @click="searchMessages">
          <span class="material-symbols-rounded">search</span> 搜索
        </button>
        <button class="bg-gray-500 text-white px-4 py-2 rounded-lg flex items-center gap-2" @click="resetFilters">
          <span class="material-symbols-rounded">refresh</span> 重置
        </button>
      </div>
    </div>

    <!-- 聊天记录列表 -->
    <div class="bg-white rounded-lg shadow">
      <div class="p-4 border-b flex items-center justify-between">
        <h3 class="text-lg font-semibold">聊天记录 ({{ messages.length }} 条)</h3>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">每页</span>
          <select v-model="pageSize" class="px-2 py-1 border border-gray-300 rounded text-sm" @change="searchMessages">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
          <span class="text-sm text-gray-500">条</span>
        </div>
      </div>
      <div class="p-4">
        <div v-if="messages.length === 0" class="text-center py-8 text-gray-500">
          <span class="material-symbols-rounded text-4xl mb-2">chat_bubble_outline</span>
          <p>暂无聊天记录</p>
        </div>
        <div v-else class="space-y-3">
          <div v-for="message in messages" :key="message.id" class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-start justify-between mb-2">
              <div class="flex items-center gap-2">
                <img :src="message.sender_avatar || defaultAvatar" class="w-8 h-8 rounded-full object-cover" alt="avatar" />
                <div>
                  <div class="font-semibold">{{ message.sender_nickname || message.sender_username }}</div>
                  <div class="text-xs text-gray-500">ID: {{ message.sender_id }}</div>
                </div>
              </div>
              <div class="text-xs text-gray-500">
                {{ formatTime(message.created_at) }}
              </div>
            </div>
            <div class="mb-2">
              <span class="inline-flex items-center text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                <span class="material-symbols-rounded text-sm mr-1">group</span>
                {{ message.group_name || `群组 ${message.group_id}` }}
              </span>
            </div>
            <div class="text-gray-700">{{ message.content }}</div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-6">
          <button 
            :disabled="currentPage === 1" 
            @click="changePage(currentPage - 1)"
            class="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-1">{{ currentPage }} / {{ totalPages }}</span>
          <button 
            :disabled="currentPage === totalPages" 
            @click="changePage(currentPage + 1)"
            class="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const defaultAvatar = 'https://api.dicebear.com/7.x/identicon/svg?seed=user'
const messages = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalPages = ref(1)

const filters = ref({
  userId: '',
  groupId: '',
  keyword: '',
  timeRange: ''
})

async function searchMessages() {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters.value
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const resp = await request.get('/api/message/list', { params })
    if (resp.data.code === 200) {
      messages.value = resp.data.data.messages || []
      totalPages.value = Math.ceil((resp.data.data.total || 0) / pageSize.value)
    }
  } catch (e) {
    console.error('获取聊天记录失败:', e)
    messages.value = []
  }
}

function resetFilters() {
  filters.value = {
    userId: '',
    groupId: '',
    keyword: '',
    timeRange: ''
  }
  currentPage.value = 1
  searchMessages()
}

function changePage(page) {
  currentPage.value = page
  searchMessages()
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

function goBack() {
  router.push('/admin/users')
}

onMounted(() => {
  searchMessages()
})
</script>

<style scoped>
</style> 