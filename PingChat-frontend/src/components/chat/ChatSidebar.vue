<script setup>
import { computed } from 'vue'
import ChatListItem from './ChatListItem.vue'
import ChatSidebarFooter from './ChatSidebarFooter.vue'

const props = defineProps(['chatList', 'currentUser', 'activeChat', 'unreadMap'])
const emit = defineEmits(['select-chat', 'group-created'])

// 排序规则
const sortedList = computed(() => {
  const hasMsg = props.chatList.filter(u => u.lastMsgTime)
    .sort((a, b) => b.lastMsgTime - a.lastMsgTime)
  const noMsg = props.chatList.filter(u => !u.lastMsgTime)
    .sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'))
  return [...hasMsg, ...noMsg]
})

function selectChat(item) {
  emit('select-chat', item)
}
function handleGroupCreated(group) {
  emit('group-created', group)  // 继续冒泡
}
</script>

<template>
  <aside class="flex flex-col h-full w-80 bg-white border-r border-gray-200">
    <div class="flex-1 overflow-y-auto py-2">
      <ChatListItem
        v-for="item in sortedList"
        :key="item.id + '-' + item.type"
        :item="item"
        :active="props.activeChat && props.activeChat.id === item.id && props.activeChat.type === item.type"
        :unreadCount="props.unreadMap?.[`${item.id}-${item.type}`] || 0"
        @click="selectChat(item)"
      />
    </div>
    <ChatSidebarFooter
      :isAdmin="props.currentUser?.is_admin"
      :ownerId="props.currentUser?.id"
      @group-created="handleGroupCreated"
    />
  </aside>
</template>