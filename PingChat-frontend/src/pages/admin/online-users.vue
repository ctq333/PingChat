<template>
  <div class="p-6">
    <!-- 页面头部 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center">
        <span class="material-symbols-rounded text-3xl text-green-500 mr-2"></span>
        <h2 class="text-4xl font-bold">在线人员管理</h2>
      </div>
      <button class="bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2" @click="goBack">
        <span class="material-symbols-rounded"></span> 返回用户管理
      </button>
    </div>

    <!-- 在线用户统计 -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-green-500">{{ onlineUsers.length }}</div>
            <div class="text-sm text-gray-500">在线用户</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-500">{{ totalUsers }}</div>
            <div class="text-sm text-gray-500">总用户数</div>
          </div>
        </div>
        <button class="bg-green-500 text-white px-4 py-2 rounded-lg flex items-center gap-2" @click="refreshData">
          <span class="material-symbols-rounded"></span> 刷新
        </button>
      </div>
    </div>

    <!-- 在线用户列表 -->
    <div class="bg-white rounded-lg shadow">
      <div class="p-4 border-b">
        <h3 class="text-lg font-semibold">在线用户列表</h3>
      </div>
      <div class="p-4">
        <div v-if="onlineUsers.length === 0" class="text-center py-8 text-gray-500">
          <span class="material-symbols-rounded text-4xl mb-2">wifi_off</span>
          <p>暂无在线用户</p>
        </div>
        <div v-else class="space-y-3">
          <div v-for="user in onlineUsers" :key="user.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
              <img :src="user.avatar_url || defaultAvatar" class="w-10 h-10 rounded-full object-cover" alt="avatar" />
              <div>
                <div class="font-semibold">{{ user.nickname || user.username }}</div>
                <div class="text-sm text-gray-500">ID: {{ user.id }} | 用户名: {{ user.username }}</div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="inline-flex items-center text-green-500 text-xs font-semibold">
                <span class="material-symbols-rounded text-base mr-1">wifi</span> 在线
              </span>
              <button class="bg-red-500 text-white px-3 py-1 rounded text-sm" @click="forceOffline(user)">
                <span class="material-symbols-rounded text-sm mr-1"></span> 强制下线
              </button>
            </div>
          </div>
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
const onlineUsers = ref([])
const totalUsers = ref(0)

async function fetchOnlineUsers() {
  try {
    const resp = await request.get('/api/user/online_list')
    if (resp.data.code === 200) {
      onlineUsers.value = resp.data.data
    }
  } catch (e) {
    console.error('获取在线用户失败:', e)
  }
}

async function fetchTotalUsers() {
  try {
    const resp = await request.get('/api/user/list')
    if (resp.data.code === 200) {
      totalUsers.value = resp.data.data.length
    }
  } catch (e) {
    console.error('获取用户总数失败:', e)
  }
}

async function forceOffline(user) {
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

<style scoped>
</style> 