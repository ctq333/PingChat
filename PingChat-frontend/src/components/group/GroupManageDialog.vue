<script setup>
import { ref, watch } from 'vue'
import request from '@/utils/request'

const props = defineProps({
  show: Boolean,
  chat: Object,
  initialTab: {
    type: String,
    default: 'remove'
  }
})
const emit = defineEmits(['close', 'group-dissolved', 'member-changed'])

const manageTab = ref(props.initialTab)
const groupMembers = ref([])
const addableUsers = ref([])
const showDissolveDialog = ref(false)

async function fetchGroupMembers() {
  if (!props.chat?.id) return
  const resp = await request.get('/api/group/members', { params: { group_id: props.chat.id } })
  groupMembers.value = resp.data.data || []
}
async function fetchAddableUsers() {
  if (!props.chat?.id) return
  const resp = await request.get('/api/group/addable_users', { params: { group_id: props.chat.id } })
  addableUsers.value = resp.data.data || []
}
async function addGroupMember(userId) {
  addableUsers.value = addableUsers.value.filter(u => u.id !== userId)
  await request.post('/api/group/add_member', { group_id: props.chat.id, user_id: userId })
  fetchGroupMembers()
  emit('member-changed')
}
async function removeGroupMember(userId) {
  groupMembers.value = groupMembers.value.filter(m => m.id !== userId)
  await request.post('/api/group/remove_member', { group_id: props.chat.id, user_id: userId })
  emit('member-changed')
}
async function dissolveGroup() {
  showDissolveDialog.value = false
  emit('close')
  try {
    await request.post('/api/group/dissolve', { group_id: props.chat.id })
    emit('group-dissolved')
  } catch (e) { }
}
function openDissolveDialog() { showDissolveDialog.value = true }
function closeDissolveDialog() { showDissolveDialog.value = false }
function closeDialog() { emit('close') }
function switchManageTab(tab) {
  manageTab.value = tab
  if (tab === 'remove') fetchGroupMembers()
  else fetchAddableUsers()
}

watch(() => props.show, (val) => {
  if (val) {
    manageTab.value = 'remove'
    fetchGroupMembers()
  }
})
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <!-- 主弹窗整体圆角，底部按钮区不被遮住 -->
    <div class="relative w-full max-w-md sm:max-w-lg flex flex-col rounded-2xl shadow-2xl bg-white animate-fade-in overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-5 border-b border-gray-100">
        <div class="flex items-center gap-2">
          <UIcon name="material-symbols:group" class="size-6 text-blue-500" />
          <span class="text-lg font-semibold text-gray-900">群成员管理</span>
        </div>
        <button
          class="p-2 rounded-full hover:bg-blue-50 text-gray-400 hover:text-blue-500 transition"
          @click="closeDialog"
        >
          <UIcon name="material-symbols:close" class="size-6" />
        </button>
      </div>

      <!-- Tab 切换 -->
      <div class="flex gap-2 px-6 pt-4 pb-1">
        <button
          class="flex-1 py-2 rounded-lg font-semibold text-sm transition-all duration-150 flex items-center justify-center gap-1"
          :class="manageTab === 'remove'
            ? 'bg-blue-500 text-white shadow'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          @click="switchManageTab('remove')"
        >
          <UIcon name="material-symbols:person-remove-outline" class="size-5" />
          成员列表
        </button>
        <button
          class="flex-1 py-2 rounded-lg font-semibold text-sm transition-all duration-150 flex items-center justify-center gap-1"
          :class="manageTab === 'add'
            ? 'bg-blue-500 text-white shadow'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          @click="switchManageTab('add')"
        >
          <UIcon name="material-symbols:person-add-outline" class="size-5" />
          添加成员
        </button>
      </div>

      <!-- 主内容区，底部有留白 -->
      <div class="flex-1 min-h-[200px] max-h-[50vh] overflow-y-auto px-6 pt-3 pb-2">
        <!-- 成员管理 -->
        <template v-if="manageTab === 'remove'">
          <ul>
            <li v-for="m in groupMembers" :key="m.id"
                class="group flex items-center justify-between gap-2 py-3 border-b last:border-b-0 border-gray-100">
              <div class="flex items-center gap-3 min-w-0">
                <div
                  class="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-base shrink-0"
                >
                  {{ m.name?.[0] || 'U' }}
                </div>
                <div class="min-w-0">
                  <div class="truncate text-gray-900 font-medium">{{ m.name }}</div>
                  <div class="flex items-center gap-1 mt-0.5">
                    <span v-if="m.is_admin"
                          class="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700 border border-blue-100 font-semibold">
                      <UIcon name="material-symbols:shield-person-outline" class="size-4 mr-1" />
                      管理员
                    </span>
                    <span v-else
                          class="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-50 text-gray-500 border border-gray-100">
                      <UIcon name="material-symbols:person-outline" class="size-4 mr-1" />
                      成员
                    </span>
                  </div>
                </div>
              </div>
              <button
                class="p-1.5 rounded-full hover:bg-red-50 text-gray-400 hover:text-red-500 transition flex items-center justify-center"
                @click="removeGroupMember(m.id)"
                title="移除成员"
              >
                <UIcon name="material-symbols:person-remove-outline" class="size-5" />
              </button>
            </li>
            <li v-if="groupMembers.length === 0" class="text-gray-400 text-center py-10">
              暂无成员
            </li>
          </ul>
        </template>
        <!-- 添加成员 -->
        <template v-else>
          <ul>
            <li v-for="u in addableUsers" :key="u.id"
                class="group flex items-center justify-between gap-2 py-3 border-b last:border-b-0 border-gray-100">
              <div class="flex items-center gap-3 min-w-0">
                <div
                  class="w-9 h-9 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold text-base shrink-0"
                >
                  {{ u.name?.[0] || 'U' }}
                </div>
                <div class="min-w-0">
                  <div class="truncate text-gray-900 font-medium">{{ u.name }}</div>
                </div>
              </div>
              <button
                class="p-1.5 rounded-full hover:bg-blue-50 text-gray-400 hover:text-blue-500 transition flex items-center justify-center"
                @click="addGroupMember(u.id)"
                title="添加成员"
              >
                <UIcon name="material-symbols:person-add-outline" class="size-5" />
              </button>
            </li>
            <li v-if="addableUsers.length === 0" class="text-gray-400 text-center py-10">
              暂无可添加成员
            </li>
          </ul>
        </template>
      </div>

      <!-- 底部按钮区，圆角只给底部，且永远可见 -->
      <div class="px-6 pb-5 pt-3 bg-gray-50 border-t border-gray-100 rounded-b-2xl">
        <button
          class="flex items-center gap-1 px-3 py-2 rounded-lg text-red-600 border border-red-100 hover:bg-red-50 transition font-medium w-full justify-center"
          @click="openDissolveDialog"
        >
          <UIcon name="material-symbols:delete-outline" class="size-5" />
          解散群聊
        </button>
      </div>

      <!-- 解散群聊确认弹窗 -->
      <div v-if="showDissolveDialog" class="fixed inset-0 z-60 flex items-center justify-center bg-black/40">
        <div class="bg-white rounded-xl shadow-lg w-full max-w-xs p-6 relative flex flex-col items-center">
          <h3 class="text-lg font-bold mb-2 text-center">解散群聊</h3>
          <p class="text-gray-700 text-sm mb-6 text-center">确定要解散该群聊吗？此操作不可恢复！</p>
          <div class="flex w-full space-x-3">
            <button class="flex-1 py-2 rounded bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold"
              @click="closeDissolveDialog">取消</button>
            <button class="flex-1 py-2 rounded bg-red-500 hover:bg-red-600 text-white font-semibold"
              @click="dissolveGroup">确定</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.18s cubic-bezier(.45,.85,.5,1.4);
}
@keyframes fadeIn {
  from { opacity:0; transform: translateY(24px);}
  to { opacity:1; transform: none;}
}
</style>