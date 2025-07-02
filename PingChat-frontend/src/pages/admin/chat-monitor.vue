<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const defaultAvatar = 'https://api.dicebear.com/7.x/identicon/svg?seed=user'

const totalPages = ref(1)

const filters = ref({
  userId: '',
  groupId: '',
  keyword: '',
  timeRange: ''
})

const timeItems = [
  { label: '全部时间', value: 'all' },
  { label: '最近1小时', value: '1h' },
  { label: '最近24小时', value: '24h' },
  { label: '最近7天', value: '7d' },
  { label: '最近30天', value: '30d' }
]

const pageItems = [
  { label: '10 条', value: 10 },
  { label: '20 条', value: 20 },
  { label: '50 条', value: 50 },
  { label: '100 条', value: 100 }
]



const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const messages = ref<any[]>([])

async function searchMessages() {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters.value
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    const resp = await request.get('/api/message/list', { params })
    if (resp.data.code === 200) {
      messages.value = resp.data.data.messages || []
      totalCount.value = resp.data.data.total || 0
    }
  } catch (e) {
    messages.value = []
    totalCount.value = 0
  }
}

// 监听分页和每页条数变化
watch([currentPage, pageSize], () => {
  searchMessages()
})

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

function changePage(page: number) {
  currentPage.value = page
  searchMessages()
}

function formatTime(timestamp: number | string) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

function goBack() {
  router.push('/admin')
}

// Watch for pageSize changes
watch(pageSize, () => {
  currentPage.value = 1 // Reset to first page when changing page size
  searchMessages()
})

onMounted(() => {
  searchMessages()
})
</script>

<template>
  <div class="p-4 md:p-8 bg-gray-50 min-h-screen">
    <!-- 页面头部 -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-2">
        <UIcon name="material-symbols:monitor-heart" class="size-7 text-green-500" />
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900">聊天记录监控</h2>
      </div>
      <UButton color="primary" variant="soft" icon="material-symbols:arrow-back-rounded" @click="goBack">
        返回管理界面
      </UButton>
    </div>

    <!-- 筛选条件 -->
    <UCard class="mb-7">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <UInput
          v-model="filters.userId"
          type="number"
          placeholder="输入用户ID"
          label="用户ID"
          :ui="{ base: 'w-full' }"
        />
        <UInput
          v-model="filters.groupId"
          type="number"
          placeholder="输入群组ID"
          label="群组ID"
          :ui="{ base: 'w-full' }"
        />
        <UInput
          v-model="filters.keyword"
          placeholder="搜索消息内容"
          label="关键词"
          :ui="{ base: 'w-full' }"
        />
        <USelect
          v-model="filters.timeRange"
          :items="timeItems"
          placeholder="全部时间"
          class="w-full"
        />
      </div>
      <div class="flex gap-2 mt-4">
        <UButton color="primary" icon="material-symbols:search" @click="searchMessages">搜索</UButton>
        <UButton color="gray" icon="material-symbols:refresh" variant="soft" @click="resetFilters">重置</UButton>
      </div>
    </UCard>

    <!-- 聊天记录列表 -->
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="material-symbols:chat-bubble-outline" class="size-5 text-blue-400" />
            <span class="text-base font-semibold">聊天记录 <span class="text-blue-600 font-bold">{{ totalCount }}</span> 条</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-xs text-gray-500">每页</span>
            <USelect v-model="pageSize" :items="pageItems" size="xs" class="w-24" />
          </div>
        </div>
      </template>
      <div>
        <div v-if="messages.length === 0" class="flex flex-col items-center py-20 text-gray-400">
          <UIcon name="material-symbols:chat-bubble-outline" class="size-9 mb-3" />
          <div>暂无聊天记录</div>
        </div>
        <div v-else class="space-y-4">
          <UCard
            v-for="message in messages"
            :key="message.id"
            class="bg-gray-50 border border-gray-100 rounded-xl"
          >
            <div class="flex items-start justify-between gap-3 mb-2">
              <div class="flex items-center gap-2">
                <UAvatar :src="message.sender_avatar || defaultAvatar" size="md" class="shadow-sm" />
                <div>
                  <div class="font-medium text-gray-900">{{ message.sender_nickname || message.sender_username }}</div>
                  <div class="text-xs text-gray-400">ID: {{ message.sender_id }}</div>
                </div>
              </div>
              <div class="text-xs text-gray-500 mt-1 shrink-0">
                {{ formatTime(message.created_at) }}
              </div>
            </div>
            <div class="mb-2">
              <span class="inline-flex items-center text-xs text-blue-700 bg-blue-50 px-2 py-1 rounded-md">
                <UIcon name="material-symbols:group" class="size-4 mr-1" />
                {{ message.group_name || `群组 ${message.group_id}` }}
              </span>
            </div>
            <div class="text-gray-800 whitespace-pre-wrap break-words text-sm leading-relaxed">{{ message.content }}</div>
          </UCard>
        </div>
        <!-- 分页 -->
        <UPagination
          v-if="totalCount > pageSize"
          v-model:page="currentPage"
          :total="totalCount"
          :items-per-page="pageSize"
          :sibling-count="2"
          :show-edges="true"
          class="mx-auto"
        />
      </div>
    </UCard>
  </div>
</template>