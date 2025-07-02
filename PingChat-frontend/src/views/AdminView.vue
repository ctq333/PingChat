<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const panels = [
  {
    label: '用户管理',
    desc: '管理用户账号、设置管理员权限、禁用/启用、禁言功能等',
    icon: 'material-symbols:group',
    iconBg: 'bg-blue-50 text-blue-600',
    to: '/admin/users',
    tip: '管理用户账号、权限和状态'
  },
  {
    label: '在线人员',
    desc: '实时查看在线用户、强制下线、监控用户活动',
    icon: 'material-symbols:online-prediction',
    iconBg: 'bg-green-50 text-green-600',
    to: '/admin/online-users',
    tip: '查看在线用户和强制下线'
  },
  {
    label: '聊天记录',
    desc: '查看所有聊天记录、筛选、关键词搜索、时间范围查询',
    icon: 'material-symbols:monitor-heart',
    iconBg: 'bg-purple-50 text-purple-600',
    to: '/admin/chat-monitor',
    tip: '查看和搜索聊天记录'
  },
  
]

function jump(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="p-6 min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-8">
      <UIcon name="material-symbols:admin-panel-settings" class="size-8 text-primary" />
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900">管理员控制台</h1>
    </div>

    <!-- 网格卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <UCard
        v-for="panel in panels"
        :key="panel.label"
        class="cursor-pointer group transition-all border border-gray-100 hover:border-blue-300 hover:shadow-md bg-white rounded-2xl"
        @click="jump(panel.to)"
      >
        <div class="flex items-center gap-4 mb-2">
          <div :class="['rounded-xl p-3', panel.iconBg, 'transition group-hover:scale-105']">
            <UIcon :name="panel.icon" class="size-7" />
          </div>
          <div>
            <div class="text-lg font-semibold text-gray-900 group-hover:text-primary transition">
              {{ panel.label }}
            </div>
            <div class="text-gray-500 text-xs mt-0.5">{{ panel.tip }}</div>
          </div>
        </div>
        <div class="text-gray-500 text-sm mt-2 leading-relaxed">
          {{ panel.desc }}
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
.text-primary {
  color: #2563eb;
}
.bg-primary {
  background-color: #2563eb;
}
</style>