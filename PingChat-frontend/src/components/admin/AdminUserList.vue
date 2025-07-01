<template>
    <div class="p-6">
      <!-- 页面顶部操作按钮 -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center">
          <span class="material-symbols-rounded text-4xl text-primary mr-2">group</span>
          <h2 class="text-3xl font-bold">用户管理</h2>
        </div>
        <div class="flex gap-3">
          <button class="bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2" @click="goToOnlineUsers">
            <span class="material-symbols-rounded"></span> 在线人员查看
          </button>
          <button class="bg-green-500 text-white px-4 py-2 rounded-lg flex items-center gap-2" @click="goToChatMonitor">
            <span class="material-symbols-rounded"></span> 聊天记录查看
          </button>
        </div>
      </div>

      <!-- 用户总数 -->
      <div class="flex items-center mb-6">
        <span class="ml-auto text-lg text-gray-500">共 {{ users.length }} 人</span>
      </div>
  
      <!-- 管理员区 -->
      <div class="mb-8">
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <span class="material-symbols-rounded text-green-500">verified_user</span> 管理员 ({{ admins.length }})
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <div v-for="user in admins" :key="user.id" class="bg-white rounded-2xl shadow-lg p-6 flex flex-col items-center border hover:shadow-2xl transition">
            <img :src="user.avatar_url || defaultAvatar" class="w-20 h-20 rounded-full object-cover border-2 border-primary mb-3" alt="avatar" />
            <div class="font-bold text-lg text-gray-900 mb-1 truncate">{{ user.nickname || user.username }}</div>
            <div class="text-gray-500 text-sm mb-2 truncate">用户名：{{ user.username }}</div>
            <div class="mb-2">
              <span class="inline-flex items-center text-green-500 text-xs font-semibold">
                <span class="material-symbols-rounded text-base mr-1">w</span> 管理员
              </span>
            </div>
            <div class="flex gap-2 mt-2">
              <button class="bg-red-50 text-red-500 px-3 py-1 rounded hover:bg-red-100 flex items-center gap-1 text-xs" @click="removeAdmin(user)">
                <span class="material-symbols-rounded text-sm"></span> 移除管理员
              </button>
              <button class="bg-gray-50 text-gray-400 px-3 py-1 rounded hover:bg-gray-100 flex items-center gap-1 text-xs" @click="deleteUser(user)">
                <span class="material-symbols-rounded text-sm"></span> 删除
              </button>
              <button v-if="!user.is_banned" class="bg-yellow-50 text-yellow-600 px-3 py-1 rounded hover:bg-yellow-100 flex items-center gap-1 text-xs" @click="banUser(user)">
                <span class="material-symbols-rounded text-sm"></span> 禁用
              </button>
              <button v-else class="bg-green-50 text-green-600 px-3 py-1 rounded hover:bg-green-100 flex items-center gap-1 text-xs" @click="unbanUser(user)">
                <span class="material-symbols-rounded text-sm"></span> 启用
              </button>
              <!-- 禁言按钮 -->
              <button
                :class="user.is_muted ? 'bg-green-50 text-green-600 px-3 py-1 rounded hover:bg-green-100 flex items-center gap-1 text-xs' : 'bg-yellow-50 text-yellow-600 px-3 py-1 rounded hover:bg-yellow-100 flex items-center gap-1 text-xs'"
                @click="toggleMute(user)"
              >
                <span class="material-symbols-rounded text-sm"></span> {{ user.is_muted ? '解除禁言' : '禁言' }}
              </button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 普通用户区 -->
      <div>
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <span class="material-symbols-rounded text-gray-400">person</span> 普通用户 ({{ normals.length }})
        </h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <div v-for="user in normals" :key="user.id" class="bg-white rounded-2xl shadow-lg p-6 flex flex-col items-center border hover:shadow-2xl transition">
            <img :src="user.avatar_url || defaultAvatar" class="w-20 h-20 rounded-full object-cover border-2 border-primary mb-3" alt="avatar" />
            <div class="font-bold text-lg text-gray-900 mb-1 truncate">{{ user.nickname || user.username }}</div>
            <div class="text-gray-500 text-sm mb-2 truncate">用户名：{{ user.username }}</div>
            <div class="mb-2">
              <span class="inline-flex items-center text-gray-400 text-xs font-semibold">
                <span class="material-symbols-rounded text-base mr-1">person</span> 普通用户
              </span>
            </div>
            <div class="flex gap-2 mt-2">
              <button class="bg-green-50 text-green-600 px-3 py-1 rounded hover:bg-green-100 flex items-center gap-1 text-xs" @click="setAdmin(user)">
                <span class="material-symbols-rounded text-sm"></span> 设为管理员
              </button>
              <button class="bg-gray-50 text-gray-400 px-3 py-1 rounded hover:bg-gray-100 flex items-center gap-1 text-xs" @click="deleteUser(user)">
                <span class="material-symbols-rounded text-sm"></span> 删除
              </button>
              <button v-if="!user.is_banned" class="bg-yellow-50 text-yellow-600 px-3 py-1 rounded hover:bg-yellow-100 flex items-center gap-1 text-xs" @click="banUser(user)">
                <span class="material-symbols-rounded text-sm"></span> 禁用
              </button>
              <button v-else class="bg-green-50 text-green-600 px-3 py-1 rounded hover:bg-green-100 flex items-center gap-1 text-xs" @click="unbanUser(user)">
                <span class="material-symbols-rounded text-sm"></span> 启用
              </button>
              <!-- 禁言按钮 -->
              <button
                :class="user.is_muted ? 'bg-green-50 text-green-600 px-3 py-1 rounded hover:bg-green-100 flex items-center gap-1 text-xs' : 'bg-yellow-50 text-yellow-600 px-3 py-1 rounded hover:bg-yellow-100 flex items-center gap-1 text-xs'"
                @click="toggleMute(user)"
              >
                <span class="material-symbols-rounded text-sm"></span> {{ user.is_muted ? '解除禁言' : '禁言' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 在线用户区 -->
      <div class="mt-10">
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <span class="material-symbols-rounded text-green-500">online_prediction</span> 在线用户 ({{ onlineUsers.length }})
        </h3>
        <ul>
          <li v-for="user in onlineUsers" :key="user.id" class="flex items-center gap-2 mb-2">
            <span>{{ user.nickname || user.username }} (ID: {{ user.id }})</span>
            <AdminUserActions :userId="user.id" @offline="fetchOnlineUsers" />
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import request from '@/utils/request'
  import AdminUserActions from './AdminUserActions.vue'
  import { useRouter } from 'vue-router'

  const router = useRouter()
  const defaultAvatar = 'https://api.dicebear.com/7.x/identicon/svg?seed=user'
  const users = ref([])
  
  const admins = computed(() => users.value.filter(u => u.is_admin))
  const normals = computed(() => users.value.filter(u => !u.is_admin))
  const onlineUsers = ref([])
  
  async function fetchUsers() {
    try {
      const resp = await request.get('/api/user/list')
      if (resp.data.code === 200) {
        users.value = resp.data.data
      } else {
        users.value = []
      }
    } catch (e) {
      users.value = []
    }
  }
  
  async function setAdmin(user) {
    await request.post('/api/user/set_admin', { id: user.id, is_admin: 1 })
    await fetchUsers()
  }
  async function removeAdmin(user) {
    await request.post('/api/user/set_admin', { id: user.id, is_admin: 0 })
    await fetchUsers()
  }
  async function deleteUser(user) {
    await request.post('/api/user/delete', { id: user.id })
    await fetchUsers()
  }
  async function banUser(user) {
    const resp = await request.post('/api/user/ban', { id: user.id })
    if (resp.data.code === 200) {
      alert('您已成功禁用此账号')
    } else {
      alert(resp.data.msg || '禁用失败')
    }
    await fetchUsers()
  }
  async function unbanUser(user) {
    await request.post('/api/user/unban', { id: user.id })
    await fetchUsers()
  }
  
  // 禁言功能
  async function toggleMute(user) {
    if (user.is_muted) {
      const resp = await request.post('/api/user/unmute', { id: user.id })
      if (resp.data.code === 200) {
        alert('已解除禁言')
        await fetchUsers()
      } else {
        alert(resp.data.msg || '操作失败')
      }
    } else {
      const resp = await request.post('/api/user/mute', { id: user.id })
      if (resp.data.code === 200) {
        alert('已禁言该用户')
        await fetchUsers()
      } else {
        alert(resp.data.msg || '操作失败')
      }
    }
  }
  
  async function fetchOnlineUsers() {
    const resp = await request.get('/api/user/online_list')
    if (resp.data.code === 200) {
      onlineUsers.value = resp.data.data
    }
  }

  // 页面跳转
  function goToOnlineUsers() {
    router.push('/admin/online-users')
  }
  
  function goToChatMonitor() {
    router.push('/admin/chat-monitor')
  }
  
  onMounted(() => {
    fetchUsers()
    fetchOnlineUsers()
  })
  </script>
  
  <style scoped>
  .bg-primary {
    background-color: #2563eb;
  }
  .bg-primary-600 {
    background-color: #1d4ed8;
  }
  .border-primary {
    border-color: #2563eb;
  }
  </style>
  