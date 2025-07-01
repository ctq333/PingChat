<template>
  <div class="p-6">
    <!-- 页面头部 -->
    <div class="flex items-center mb-8">
      <span class="material-symbols-rounded text-4xl text-primary mr-3">admin_panel_settings</span>
      <h1 class="text-3xl font-bold">管理员控制台</h1>
    </div>

    <!-- 功能卡片网格 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- 用户管理 -->
      <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" @click="goToUsers">
        <div class="flex items-center mb-4">
          <div class="bg-blue-100 p-3 rounded-lg">
            <span class="material-symbols-rounded text-2xl text-blue-600">group</span>
          </div>
          <div class="ml-4">
            <h3 class="text-xl font-semibold text-gray-900">用户管理</h3>
            <p class="text-gray-500 text-sm">管理用户账号、权限和状态</p>
          </div>
        </div>
        <div class="text-sm text-gray-600">
          管理用户账号、设置管理员权限、禁用/启用用户、禁言功能等
        </div>
      </div>

      <!-- 在线人员查看 -->
      <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" @click="goToOnlineUsers">
        <div class="flex items-center mb-4">
          <div class="bg-green-100 p-3 rounded-lg">
            <span class="material-symbols-rounded text-2xl text-green-600">online_prediction</span>
          </div>
          <div class="ml-4">
            <h3 class="text-xl font-semibold text-gray-900">在线人员</h3>
            <p class="text-gray-500 text-sm">查看在线用户和强制下线</p>
          </div>
        </div>
        <div class="text-sm text-gray-600">
          实时查看在线用户列表、强制用户下线、监控用户活动
        </div>
      </div>

      <!-- 聊天记录监控 -->
      <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" @click="goToChatMonitor">
        <div class="flex items-center mb-4">
          <div class="bg-purple-100 p-3 rounded-lg">
            <span class="material-symbols-rounded text-2xl text-purple-600">monitor_heart</span>
          </div>
          <div class="ml-4">
            <h3 class="text-xl font-semibold text-gray-900">聊天记录</h3>
            <p class="text-gray-500 text-sm">查看和搜索聊天记录</p>
          </div>
        </div>
        <div class="text-sm text-gray-600">
          查看所有聊天记录、按用户/群组筛选、关键词搜索、时间范围查询
        </div>
      </div>

      <!-- 群组管理
      <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" @click="goToGroupManage">
        <div class="flex items-center mb-4">
          <div class="bg-orange-100 p-3 rounded-lg">
            <span class="material-symbols-rounded text-2xl text-orange-600">forum</span>
          </div>
          <div class="ml-4">
            <h3 class="text-xl font-semibold text-gray-900">群组管理</h3>
            <p class="text-gray-500 text-sm">管理聊天群组</p>
          </div>
        </div>
        <div class="text-sm text-gray-600">
          创建群组、管理群成员、设置群组权限、查看群组信息
        </div>
      </div> -->

      <!-- 数据导出
      <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" @click="goToExport">
        <div class="flex items-center mb-4">
          <div class="bg-red-100 p-3 rounded-lg">
            <span class="material-symbols-rounded text-2xl text-red-600">download</span>
          </div>
          <div class="ml-4">
            <h3 class="text-xl font-semibold text-gray-900">数据导出</h3>
            <p class="text-gray-500 text-sm">导出系统数据</p>
          </div>
        </div>
        <div class="text-sm text-gray-600">
          导出用户数据、聊天记录、群组信息等系统数据
        </div>
      </div> -->

      <!-- 系统设置 -->
      <!-- <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" @click="goToSettings">
        <div class="flex items-center mb-4">
          <div class="bg-gray-100 p-3 rounded-lg">
            <span class="material-symbols-rounded text-2xl text-gray-600">settings</span>
          </div>
          <div class="ml-4">
            <h3 class="text-xl font-semibold text-gray-900">系统设置</h3>
            <p class="text-gray-500 text-sm">系统配置和参数</p>
          </div>
        </div>
        <div class="text-sm text-gray-600">
          系统参数配置、安全设置、功能开关等管理选项
        </div>
      </div> -->
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToUsers() {
  router.push('/admin/users')
}

function goToOnlineUsers() {
  router.push('/admin/online-users')
}

function goToChatMonitor() {
  router.push('/admin/chat-monitor')
}

function goToGroupManage() {
  router.push('/group')
}

function goToExport() {
  router.push('/export')
}

function goToSettings() {
  // 暂时跳转到用户管理页面
  router.push('/admin/users')
}
</script>

<style scoped>
.bg-primary {
  background-color: #2563eb;
}
</style>