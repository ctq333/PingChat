<script setup>
import IconSettings from '~icons/material-symbols/settings-outline'
import IconAdd from '~icons/material-symbols/add'
import IconLogout from '~icons/material-symbols/logout'
import IconAdminPanelSettings from '~icons/material-symbols/admin-panel-settings'
import IconTune from '~icons/material-symbols/tune'
import IconExport from '~icons/material-symbols/download' // 用 Material Symbols 的下载/导出图标
import { ref } from 'vue'

const props = defineProps({ isAdmin: Boolean })
const showMenu = ref(false)
function toggleMenu() { showMenu.value = !showMenu.value }

function handleMenu(action) {
  showMenu.value = false
  if (action === 'export') {
    // 这里触发导出聊天记录逻辑
    // 你可以 emit 事件，或者直接调用导出逻辑
    alert('导出聊天记录功能待实现')
  }
}
function handleAddGroup() {}
</script>

<template>
  <div class="relative flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-white">
    <div class="relative">
      <button
        class="flex items-center justify-center text-gray-500 hover:text-blue-600 p-2"
        @click="toggleMenu"
      >
        <IconSettings class="w-6 h-6" />
      </button>
      <div v-if="showMenu"
        class="absolute z-10 left-0 bottom-12 min-w-[140px] rounded shadow bg-white border border-gray-200 py-2"
      >
        <button @click="handleMenu('logout')" class="flex w-full items-center px-4 py-2 text-gray-700 hover:bg-blue-50 text-sm">
          <IconLogout class="w-5 h-5 mr-2" />退出登录
        </button>
        <button @click="handleMenu('settings')" class="flex w-full items-center px-4 py-2 text-gray-700 hover:bg-blue-50 text-sm">
          <IconTune class="w-5 h-5 mr-2" />系统设置
        </button>
        <button @click="handleMenu('export')" class="flex w-full items-center px-4 py-2 text-gray-700 hover:bg-blue-50 text-sm">
          <IconExport class="w-5 h-5 mr-2" />导出聊天记录
        </button>
        <button v-if="isAdmin" @click="handleMenu('admin')" class="flex w-full items-center px-4 py-2 text-gray-700 hover:bg-blue-50 text-sm">
          <IconAdminPanelSettings class="w-5 h-5 mr-2" />管理员界面
        </button>
      </div>
    </div>
    <button
      class="flex items-center justify-center text-blue-600 hover:text-blue-800 p-2"
      @click="handleAddGroup"
    >
      <IconAdd class="w-7 h-7" />
    </button>
  </div>
</template>