<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const defaultAvatar = 'https://api.dicebear.com/7.x/identicon/svg?seed=user'
const onlineUsers = ref<any[]>([])
const totalUsers = ref(0)
let intervalId: any = null

function startPolling() {
  // 每5秒自动拉取一次
  intervalId = setInterval(() => {
    fetchOnlineUsers()
  }, 5000)
}

function stopPolling() {
  if (intervalId) clearInterval(intervalId)
}

onMounted(() => {
  fetchOnlineUsers()
  fetchTotalUsers()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

async function fetchOnlineUsers() {
  try {
    const resp = await request.get('/api/user/online_list')
    if (resp.data.code === 200) {
      onlineUsers.value = resp.data.data
    }
  } catch (e) {
    onlineUsers.value = []
  }
}

async function fetchTotalUsers() {
  try {
    const resp = await request.get('/api/user/list')
    if (resp.data.code === 200) {
      totalUsers.value = resp.data.data.length
    }
  } catch (e) {
    totalUsers.value = 0
  }
}

async function forceOffline(user: any) {
  if (confirm(`确定要强制用户 ${user.nickname || user.username} 下线吗？`)) {
    try {
      const resp = await request.post('/api/user/kick', { id: user.id })
      if (resp.data.code === 200) {
        alert('已强制用户下线')
        await fetchOnlineUsers()
      } else {
        alert(resp.data.msg || '操作失败')
      }
    } catch (e) {
      alert('操作失败')
    }
  }
}

function refreshData() {
  fetchOnlineUsers()
  fetchTotalUsers()
}

function goBack() {
  router.push('/admin/users')
}

onMounted(() => {
  fetchOnlineUsers()
  fetchTotalUsers()
})
</script>

<template>
  <div class="p-4 md:p-8 bg-gray-50 min-h-screen">
    <!-- 页面头部 -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-8">
      <div class="flex items-center gap-3">
        <UIcon name="material-symbols:wifi" class="size-8 text-green-500" />
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900">在线人员管理</h2>
      </div>
      <UButton color="primary" variant="soft" icon="material-symbols:arrow-back-rounded" @click="goBack">
        返回用户管理
      </UButton>
    </div>

    <!-- 在线用户统计 -->
    <UCard class="mb-7">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex flex-wrap gap-6">
          <div class="flex flex-col items-center px-3">
            <UIcon name="material-symbols:wifi" class="size-7 text-green-500 mb-1" />
            <div class="text-2xl font-bold text-green-600">{{ onlineUsers.length }}</div>
            <div class="text-xs text-gray-500 mt-1">在线用户</div>
          </div>
          <div class="flex flex-col items-center px-3">
            <UIcon name="material-symbols:group" class="size-7 text-blue-500 mb-1" />
            <div class="text-2xl font-bold text-blue-600">{{ totalUsers }}</div>
            <div class="text-xs text-gray-500 mt-1">总用户数</div>
          </div>
        </div>
        <UButton color="green" icon="material-symbols:refresh" variant="soft" @click="refreshData">
          刷新
        </UButton>
      </div>
    </UCard>

    <!-- 在线用户列表 -->
    <UCard>
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon name="material-symbols:wifi" class="size-5 text-green-500" />
          <span class="font-semibold text-base">在线用户列表</span>
        </div>
      </template>
      <div>
        <div v-if="onlineUsers.length === 0" class="flex flex-col items-center py-20 text-gray-400">
          <UIcon name="material-symbols:wifi-off" class="size-10 mb-3" />
          <div>暂无在线用户</div>
        </div>
        <div v-else class="space-y-3">
          <UCard
            v-for="user in onlineUsers"
            :key="user.id"
            class="bg-gray-50 border border-gray-100 rounded-xl flex flex-col sm:flex-row items-center sm:items-stretch justify-between gap-4 p-4"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <UAvatar :src="user.avatar_url || defaultAvatar" size="lg" class="shadow-sm" />
              <div class="truncate">
                <div class="font-medium text-gray-900 truncate">{{ user.nickname || user.username }}</div>
                <div class="text-xs text-gray-400 truncate">ID: {{ user.id }} | 用户名: {{ user.username }}</div>
              </div>
            </div>
            <div class="flex items-center gap-3 mt-3 sm:mt-0">
              <UButton color="green" variant="outline" icon="material-symbols:wifi" size="xs" disabled>
                在线
              </UButton>
              <UButton
                color="red"
                icon="material-symbols:logout"
                size="xs"
                variant="solid"
                @click="forceOffline(user)"
              >
                强制下线
              </UButton>
            </div>
          </UCard>
        </div>
      </div>
    </UCard>
  </div>
</template>