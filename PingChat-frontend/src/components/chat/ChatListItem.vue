<script setup>
const props = defineProps({
  item: Object,
  active: Boolean,
  unreadCount: {
    type: Number,
    default: 0
  },
  isOnline: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div :class="['flex items-center cursor-pointer select-none px-4 py-2 transition',
    active ? 'bg-blue-50' : 'hover:bg-gray-100']" @click="$emit('click')">
    <div
      class="relative w-10 h-10 rounded-full mr-3 bg-gray-200 flex items-center justify-center text-lg font-bold text-gray-600">
      {{ item.name[0] }}
      <!-- 未读红点 -->
      <span v-if="unreadCount > 0 && !active"
        class="absolute -top-1.5 -right-1.5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
        style="min-width: 20px; height: 20px; padding: 0 6px; border: 2px solid #fff; box-sizing: border-box;">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
      <!-- 在线绿点，仅单聊 -->
      <span v-if="isOnline"
        class="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-green-500 border-2 border-white"></span>
    </div>
    <div class="flex-1 overflow-hidden">
      <div class="flex items-center text-sm font-medium text-gray-900">
        <span class="truncate">{{ item.name }}</span>
        <span v-if="item.type === 'group'" class="ml-2 px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-700">群组</span>
      </div>
      <div class="text-xs text-gray-400 truncate">
        {{ item.lastMsg || '暂无聊天记录' }}
      </div>
    </div>
    <div class="ml-2 text-xs text-gray-400">
      <span v-if="item.lastMsgTime">
        {{ new Date(item.lastMsgTime).toLocaleTimeString() }}
      </span>
    </div>
  </div>
</template>