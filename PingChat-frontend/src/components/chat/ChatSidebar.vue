<script setup>
import { computed } from 'vue'
import ChatListItem from './ChatListItem.vue'
import ChatSidebarFooter from './ChatSidebarFooter.vue'

const props = defineProps(['chatList', 'currentUser', 'activeChat'])
const emit = defineEmits(['select-chat'])

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
</script>

<template>
  <aside class="flex flex-col h-full w-80 bg-white border-r border-gray-200">
    <div class="flex-1 overflow-y-auto py-2">
      <ChatListItem
        v-for="item in sortedList"
        :key="item.id + '-' + item.type"
        :item="item"
        :active="props.activeChat && props.activeChat.id === item.id && props.activeChat.type === item.type"
        @click="selectChat(item)"
      />
    </div>
    <ChatSidebarFooter :isAdmin="true" />
  </aside>
</template>