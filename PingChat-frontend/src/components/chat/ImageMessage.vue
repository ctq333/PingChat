<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getImage } from '@/utils/userChatStorage' // 确保路径正确

const props = defineProps({
  senderId: {
    type: Number,
    required: true
  },
  imageId: {
    type: String,
    required: true
  }
})

// 这个 ref 将持有我们生成的 blob: URL
const imageUrl = ref('')
const isLoading = ref(true)

// 用一个变量来追踪创建的 URL，以便后续释放
let blobUrlObject = null 

onMounted(async () => {
  // 从 IndexedDB 中异步获取 blob 数据
  const blob = await getImage(props.senderId, props.imageId)
  
  if (blob) {
    // 创建一个临时的、可供 <img> 标签使用的 URL
    blobUrlObject = URL.createObjectURL(blob)
    imageUrl.value = blobUrlObject
  } else {
    // 处理图片未找到的情况，比如显示一个错误占位图
    console.error(`数据库中未找到图片: 用户 ${props.senderId}, ID ${props.imageId}`)
    imageUrl.value = 'https://via.placeholder.com/150/FF0000/FFFFFF?Text=图片加载失败'
  }
  isLoading.value = false
})

// 非常重要：组件销毁时，释放创建的 Blob URL 以防止内存泄漏
onUnmounted(() => {
  if (blobUrlObject) {
    URL.revokeObjectURL(blobUrlObject)
  }
})
</script>

<template>
  <div>
    <div v-if="isLoading" class="w-40 h-32 bg-gray-300 animate-pulse rounded-xl"></div>
    <img
      v-else
      :src="imageUrl"
      class="w-40 max-w-xs rounded-xl"
      alt="图片消息"
    />
  </div>
</template>