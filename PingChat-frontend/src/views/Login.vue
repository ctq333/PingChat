<template>
  <div class="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-200 overflow-hidden">
    <div class="w-full max-w-md mx-auto bg-white rounded-2xl shadow-lg px-8 py-10">
      <form @submit.prevent="onBtnLoginClick" class="space-y-6" autocomplete="off">
        <h2 class="text-3xl font-bold text-center mb-8 flex items-center justify-center gap-2">
          登录
        </h2>
        <!-- 用户名输入框 -->
        <UFormGroup
          :error="inputError && !account ? '请输入用户名或邮箱' : undefined"
        >
          <UInput
            v-model="account"
            size="lg"
            icon="i-heroicons-user"
            placeholder="用户名或邮箱"
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
            type="password"
            placeholder="密码"
            autocomplete="current-password"
            :ui="{ base: 'w-full', input: inputError && !password ? 'border-red-500' : '' }"
            :trailing-icon="showPassword ? 'i-heroicons-eye-off' : 'i-heroicons-eye'"
            @trailing-icon-click="showPassword = !showPassword"
            :type="showPassword ? 'text' : 'password'"
          />
        </UFormGroup>
        <!-- 注册按钮 -->
        <div class="flex justify-between items-center">
          <NuxtLink to="/signup" class="text-blue-500 hover:underline text-sm flex items-center gap-1">
            <UIcon name="i-heroicons-user-plus" class="w-4 h-4" />
            注册账号
          </NuxtLink>
        </div>
        <!-- 登录按钮 -->
        <UButton
          size="lg"
          class="w-full"
          icon="i-heroicons-arrow-right-on-rectangle"
          :loading="loading"
          @click="onBtnLoginClick"
        >
          登录
        </UButton>
        <!-- 错误提示 -->
        <div v-if="loginError" class="text-red-500 text-sm mt-4 text-center">
          {{ loginError }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import store from '@/store'
import request from '@/utils/request'

const account = ref('')
const password = ref('')
const loading = ref(false)
const loginError = ref('')
const inputError = ref(false)
const showPassword = ref(false)

const router = useRouter()

async function onBtnLoginClick() {
  loginError.value = ''
  inputError.value = false

  if (!account.value || !password.value) {
    loginError.value = '请输入用户名和密码'
    inputError.value = true
    return
  }

  loading.value = true
  try {
    const response = await request.post('/auth/login', {
      username: account.value,
      password: password.value
    })
    if (response.data.code === 200) {
      store.commit('SET_USER', response.data.data.user)
      store.commit('SET_TOKEN', response.data.data.token)
      router.push('/')
    } else {
      loginError.value = `登录失败: ${response.data.message}`
    }
  } catch (error) {
    if (error.response) {
      loginError.value = error.response.data.message || '服务器错误'
    } else {
      loginError.value = error.message
    }
  } finally {
    loading.value = false
  }
}
</script>