<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50">
    <div class="text-8xl font-bold text-blue-400 mb-6">404</div>
    <div class="text-2xl text-gray-800 mb-4">页面不存在</div>
    <div class="text-gray-500 mb-8">Oops! 你访问的页面不存在或已被删除。</div>
    <router-link
      to="/"
      class="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded shadow transition"
    >
      返回首页
    </router-link>
  </div>
</template>

<script setup>
// 无需脚本
</script>

<style scoped>
/* 可加自定义样式 */
</style>
