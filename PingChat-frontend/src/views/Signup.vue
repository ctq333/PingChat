<template>
  <div class="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-200 overflow-hidden">
    <div class="w-full max-w-md mx-auto bg-white rounded-2xl shadow-lg px-8 py-10">
      <form @submit.prevent="onRegisterClick" class="space-y-6" autocomplete="off">
        <h2 class="text-3xl font-bold text-center mb-8 flex items-center justify-center gap-2">
          注册
        </h2>
        <!-- 用户名输入框 -->
        <UFormGroup
          :error="inputError && !account ? '请输入用户名' : undefined"
        >
          <UInput
            v-model="account"
            size="lg"
            icon="i-heroicons-user"
            placeholder="用户名"
            autocomplete="username"
            :ui="{ base: 'w-full', input: inputError && !account ? 'border-red-500' : '' }"
          />
        </UFormGroup>
        <!-- 密码输入框 -->
        <UFormGroup
          :error="inputError && !password ? '请输入密码' : undefined"
        >
          <UInput
            v-model="password"
            size="lg"
            icon="i-heroicons-lock-closed"
            :type="showPassword ? 'text' : 'password'"
            placeholder="密码"
            autocomplete="new-password"
            :ui="{ base: 'w-full', input: inputError && !password ? 'border-red-500' : '' }"
            :trailing-icon="showPassword ? 'i-heroicons-eye-off' : 'i-heroicons-eye'"
            @trailing-icon-click="showPassword = !showPassword"
          />
        </UFormGroup>
        <!-- 返回登录按钮 -->
        <div class="flex justify-between items-center">
          <NuxtLink to="/login" class="text-blue-500 hover:underline text-sm flex items-center gap-1">
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            返回登录
          </NuxtLink>
        </div>
        <!-- 注册按钮 -->
        <UButton
          size="lg"
          class="w-full"
          icon="i-heroicons-user-plus"
          :loading="loading"
          @click="onRegisterClick"
        >
          注册
        </UButton>
        <!-- 错误/成功提示 -->
        <div v-if="regError" class="text-red-500 text-sm mt-4 text-center">
          {{ regError }}
        </div>
        <div v-if="regSuccess" class="text-green-600 text-sm mt-4 text-center">
          {{ regSuccess }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const account = ref('')
const password = ref('')
const loading = ref(false)
const regError = ref('')
const regSuccess = ref('')
const inputError = ref(false)
const showPassword = ref(false)

const router = useRouter()

async function onRegisterClick() {
  regError.value = ''
  regSuccess.value = ''
  inputError.value = false
  if (!account.value || !password.value) {
    regError.value = '请输入用户名和密码'
    inputError.value = true
    return
  }
  loading.value = true
  try {
    const response = await request.post('/auth/register', {
      username: account.value,
      password: password.value
    })
    if (response.data.code === 201) {
      regSuccess.value = '注册成功，正在跳转登录...'
      setTimeout(() => {
        router.push({ name: 'login' })
      }, 1000)
    } else {
      regError.value = `注册失败: ${response.data.message}`
    }
  } catch (error) {
    if (error.response) {
      regError.value = error.response.data.message || '服务器错误'
    } else {
      regError.value = error.message
    }
  } finally {
    loading.value = false
  }
}
</script>