<template>
  <div class="flex items-center gap-2">
    <!-- 在线状态显示 -->
    <span class="text-xs px-2 py-1 rounded" :class="isOnline ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'">
      {{ isOnline ? '在线' : '离线' }}
    </span>
    <!-- 强制下线按钮 -->
    <button
      v-if="isOnline"
      class="bg-red-500 text-white px-2 py-1 rounded text-xs"
      @click="forceOffline"
    >
      强制下线
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const props = defineProps({ userId: Number })
const emit = defineEmits(['offline'])
const isOnline = ref(false)

async function checkOnlineStatus() {
  try {
    const resp = await request.get(`/api/user/${props.userId}/online`)
    isOnline.value = resp.data.online
  } catch (e) {
    isOnline.value = false
  }
}

async function forceOffline() {
  const resp = await request.post('/api/user/kick', { id: props.userId })
  if (resp.data.code === 200) {
    alert('已强制用户下线')
    isOnline.value = false
    emit('offline')
  } else {
    alert(resp.data.msg || '操作失败')
  }
}

onMounted(() => {
  checkOnlineStatus()
})
</script>

<style scoped>

</style>