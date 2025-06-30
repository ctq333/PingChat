<script setup>
import { ref, watch } from 'vue'
import IconClose from '~icons/material-symbols/close'
import request from '@/utils/request'

const props = defineProps({
    show: Boolean,
    chat: Object,
    // 可选：初始tab
    initialTab: {
        type: String,
        default: 'remove'
    }
})
const emit = defineEmits(['close', 'group-dissolved', 'member-changed'])

const manageTab = ref(props.initialTab)
const groupMembers = ref([])
const addableUsers = ref([])
const showAddUserDialog = ref(false)
const showDissolveDialog = ref(false)

// 查询群成员
async function fetchGroupMembers() {
    if (!props.chat?.id) return
    const resp = await request.get('/api/group/members', { params: { group_id: props.chat.id } })
    groupMembers.value = resp.data.data || []
}
// 查询可添加用户
async function fetchAddableUsers() {
    if (!props.chat?.id) return
    const resp = await request.get('/api/group/addable_users', { params: { group_id: props.chat.id } })
    addableUsers.value = resp.data.data || []
}
// 添加成员
async function addGroupMember(userId) {
    addableUsers.value = addableUsers.value.filter(u => u.id !== userId)
    await request.post('/api/group/add_member', { group_id: props.chat.id, user_id: userId })
    fetchGroupMembers()
    emit('member-changed')
}
// 删除成员
async function removeGroupMember(userId) {
    groupMembers.value = groupMembers.value.filter(m => m.id !== userId)
    await request.post('/api/group/remove_member', { group_id: props.chat.id, user_id: userId })
    emit('member-changed')
}
// 解散群聊
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
        <div class="bg-white rounded-lg shadow-lg w-full max-w-md p-6 relative">
            <h2 class="text-lg font-bold mb-4">群成员管理</h2>
            <div class="flex items-center mb-4">
                <button class="flex-1 py-2 rounded-l-lg text-sm font-semibold transition-all duration-150"
                    :class="manageTab === 'remove' ? 'bg-blue-500 text-white shadow' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
                    @click="switchManageTab('remove')">删除成员</button>
                <button class="flex-1 py-2 rounded-r-lg text-sm font-semibold transition-all duration-150"
                    :class="manageTab === 'add' ? 'bg-blue-500 text-white shadow' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
                    @click="switchManageTab('add')">添加成员</button>
            </div>
            <div v-if="manageTab === 'remove'">
                <ul class="mb-4 max-h-60 overflow-y-auto">
                    <li v-for="m in groupMembers" :key="m.id"
                        class="flex items-center justify-between py-2 border-b last:border-b-0">
                        <span>{{ m.name }}</span>
                        <button class="text-red-500 hover:underline text-sm"
                            @click="removeGroupMember(m.id)">移除</button>
                    </li>
                </ul>
            </div>
            <div v-else>
                <ul class="mb-4 max-h-60 overflow-y-auto">
                    <li v-for="u in addableUsers" :key="u.id"
                        class="flex items-center justify-between py-2 border-b last:border-b-0">
                        <span>{{ u.name }}</span>
                        <button class="text-blue-500 hover:underline text-sm" @click="addGroupMember(u.id)">添加</button>
                    </li>
                </ul>
            </div>
            <button class="absolute top-2 right-2 text-gray-400 hover:text-gray-700" @click="closeDialog">
                <IconClose class="w-6 h-6" />
            </button>
            <!-- 解散群聊按钮 -->
            <button class="w-full mt-2 py-2 rounded bg-red-500 hover:bg-red-600 text-white font-semibold transition"
                @click="openDissolveDialog">解散群聊</button>
            <!-- 解散群聊确认弹窗 -->
            <div v-if="showDissolveDialog" class="fixed inset-0 z-60 flex items-center justify-center bg-black/40">
                <div class="bg-white rounded-lg shadow-lg w-full max-w-xs p-6 relative flex flex-col items-center">
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
