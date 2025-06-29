<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
    <div class="bg-white rounded-xl p-8 w-[350px] shadow-lg">
      <h3 class="text-lg font-bold mb-4">新建群组</h3>
      <div class="mb-3">
        <label class="block mb-1 text-sm">群名称</label>
        <input v-model="groupName" class="w-full border rounded px-2 py-1" placeholder="请输入群名称" />
      </div>
      <div class="mb-3">
        <label class="block mb-1 text-sm">选择成员</label>
        <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
          <label
            v-for="user in users"
            :key="user.id"
            class="flex items-center space-x-1"
          >
            <input
              type="checkbox"
              :value="user.id"
              v-model="selected"
              :disabled="user.id === ownerId"
            />
            <span>{{ user.nickname }}</span>
          </label>
        </div>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <button @click="close" class="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200">取消</button>
        <button
          @click="create"
          :disabled="!groupName.trim()"
          class="px-3 py-1 rounded bg-blue-500 text-white hover:bg-blue-600 disabled:bg-gray-300"
        >确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import request from '@/utils/request'

const props = defineProps({
  show: Boolean,
  ownerId: Number
})
const emit = defineEmits(['close', 'created'])

const groupName = ref('')
const users = ref([])
const selected = ref([])

watch(() => props.show, val => {
  if (val) fetchUsers()
  groupName.value = ''
  selected.value = []
})

async function fetchUsers() {
  const resp = await request.get('/api/user/list')
  users.value = resp.data.data || []
}

function close() {
  emit('close')
}

async function create() {
  if (!groupName.value.trim()) return
  const member_ids = selected.value.filter(id => id !== props.ownerId)
  const resp = await request.post('/api/group/create', {
    name: groupName.value.trim(),
    owner_id: props.ownerId,
    member_ids
  })
  if (resp.data.code === 200) {
    emit('created', {
      id: resp.data.data.group_id,
      name: groupName.value.trim()
    })
    close()
  } else {
    alert(resp.data.message || '创建失败')
  }
}

</script>