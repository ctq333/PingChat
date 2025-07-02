<script setup lang="ts">
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

<template>
  <div class="p-4 md:p-8 bg-gray-50 min-h-screen">
    <!-- 页面顶部操作按钮 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-8">
      <div class="flex items-center gap-3">
        <UIcon name="material-symbols:group" class="size-8 text-primary" />
        <h2 class="text-2xl md:text-3xl font-bold text-gray-900">用户管理</h2>
      </div>
      <div class="flex gap-2">
        <UButton color="primary" icon="material-symbols:wifi" variant="soft" @click="goToOnlineUsers">
          在线人员查看
        </UButton>
        <UButton color="green" icon="material-symbols:monitor-heart" variant="soft" @click="goToChatMonitor">
          聊天记录查看
        </UButton>
      </div>
    </div>

    <!-- 用户总数 -->
    <div class="flex items-center mb-8">
      <span class="ml-auto text-lg text-gray-500">共 {{ users.length }} 人</span>
    </div>

    <!-- 管理员区 -->
    <div class="mb-10">
      <h3 class="text-lg font-semibold mb-5 flex items-center gap-2 text-green-600">
        <UIcon name="material-symbols:verified-user" class="size-5" />
        管理员 ({{ admins.length }})
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        <UCard v-for="user in admins" :key="user.id" class="flex flex-col items-center gap-2 border border-green-100 rounded-2xl shadow hover:shadow-lg transition">
          <UAvatar :src="user.avatar_url || defaultAvatar" size="xl" class="mb-2 border-2 border-primary" />
          <div class="font-semibold text-lg text-gray-900 truncate">{{ user.nickname || user.username }}</div>
          <div class="text-gray-500 text-xs truncate">用户名：{{ user.username }}</div>
          <div class="flex items-center gap-1 mb-1 mt-1">
            <UIcon name="material-symbols:shield-person-outline" class="size-4 text-green-500" />
            <span class="text-green-600 text-xs font-semibold">管理员</span>
          </div>
          <div class="flex flex-wrap gap-2 mt-1 w-full justify-center">
            <UButton color="red" size="xs" variant="soft" icon="material-symbols:person-remove-outline" @click="removeAdmin(user)">
              移除管理员
            </UButton>
            <UButton color="gray" size="xs" variant="soft" icon="material-symbols:delete-outline" @click="deleteUser(user)">
              删除
            </UButton>
            <UButton
              v-if="!user.is_banned"
              color="yellow"
              size="xs"
              variant="soft"
              icon="material-symbols:person-off-outline"
              @click="banUser(user)"
            >禁用</UButton>
            <UButton
              v-else
              color="green"
              size="xs"
              variant="soft"
              icon="material-symbols:person-outline"
              @click="unbanUser(user)"
            >启用</UButton>
            
          </div>
        </UCard>
      </div>
    </div>

    <!-- 普通用户区 -->
    <div class="mb-10">
      <h3 class="text-lg font-semibold mb-5 flex items-center gap-2 text-gray-700">
        <UIcon name="material-symbols:person-outline" class="size-5 text-gray-400" />
        普通用户 ({{ normals.length }})
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        <UCard v-for="user in normals" :key="user.id" class="flex flex-col items-center gap-2 border border-gray-100 rounded-2xl shadow hover:shadow-lg transition">
          <UAvatar :src="user.avatar_url || defaultAvatar" size="xl" class="mb-2 border-2 border-primary" />
          <div class="font-semibold text-lg text-gray-900 truncate">{{ user.nickname || user.username }}</div>
          <div class="text-gray-500 text-xs truncate">用户名：{{ user.username }}</div>
          <div class="flex items-center gap-1 mb-1 mt-1">
            <UIcon name="material-symbols:person-outline" class="size-4 text-gray-400" />
            <span class="text-gray-500 text-xs font-semibold">普通用户</span>
          </div>
          <div class="flex flex-wrap gap-2 mt-1 w-full justify-center">
            <UButton color="green" size="xs" variant="soft" icon="material-symbols:shield-person-outline" @click="setAdmin(user)">
              设为管理员
            </UButton>
            <UButton color="gray" size="xs" variant="soft" icon="material-symbols:delete-outline" @click="deleteUser(user)">
              删除
            </UButton>
            <UButton
              v-if="!user.is_banned"
              color="yellow"
              size="xs"
              variant="soft"
              icon="material-symbols:person-off-outline"
              @click="banUser(user)"
            >禁用</UButton>
            <UButton
              v-else
              color="green"
              size="xs"
              variant="soft"
              icon="material-symbols:person-outline"
              @click="unbanUser(user)"
            >启用</UButton>
            
          </div>
        </UCard>
      </div>
    </div>

    <!-- 在线用户区 -->
    <div class="mb-10">
      <h3 class="text-lg font-semibold mb-5 flex items-center gap-2 text-blue-700">
        <UIcon name="material-symbols:online-prediction" class="size-5 text-green-500" />
        在线用户 ({{ onlineUsers.length }})
      </h3>
      <UCard v-if="onlineUsers.length" class="px-4 py-3">
        <ul class="divide-y divide-gray-100">
          <li v-for="user in onlineUsers" :key="user.id" class="flex items-center gap-2 py-2">
            <UAvatar :src="user.avatar_url || defaultAvatar" size="sm" />
            <span class="truncate flex-1">{{ user.nickname || user.username }} <span class="text-xs text-gray-400">(ID: {{ user.id }})</span></span>
            <!-- <AdminUserActions :userId="user.id" @offline="fetchOnlineUsers" /> -->
          </li>
        </ul>
      </UCard>
      <div v-else class="flex flex-col items-center py-10 text-gray-400">
        <UIcon name="material-symbols:wifi-off" class="size-8 mb-3" />
        <span>暂无在线用户</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-primary {
  color: #2563eb;
}
.border-primary {
  border-color: #2563eb;
}
</style>