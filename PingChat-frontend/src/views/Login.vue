<template>
  <div class="fixed inset-0 flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md mx-auto bg-white rounded-2xl shadow-lg px-8 py-10">
      <form @submit.prevent="onBtnLoginClick" class="space-y-6" autocomplete="off">
        <h2 class="text-3xl font-bold text-center mb-8 flex items-center justify-center gap-2">
          登录
        </h2>
        
        <!-- 用户名输入框 -->
          <UInput
            v-model="account"
            icon="material-symbols:person"
            placeholder="用户名"
            autocomplete="username"
            class="w-full h-12"
            size="xl"
            color="neutral"
            :ui="{ base: 'w-full', input: (inputError && !account ? 'border-red-500' : '') + ' w-full' }"
          />

        
        <!-- 密码输入框 -->

          <div class="relative w-full">
            <UInput
              v-model="password"
              icon="material-symbols:lock"
              :type="showPassword ? 'text' : 'password'"
              placeholder="密码"
              autocomplete="current-password"
              class="w-full pr-12"
              size="xl"
              color="neutral"
              :ui="{ base: 'w-full', input: (inputError && !password ? 'border-red-500' : '') + ' w-full pr-12' }"
            />
            <!-- 密码显示/隐藏按钮 -->
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500"
              tabindex="-1"
            >
              <UIcon :name="showPassword ? 'material-symbols:visibility-off' : 'material-symbols:visibility'" class="w-5 h-5" />
            </button>
          </div>

        
        <!-- 注册按钮 -->
        <div class="flex justify-between items-center">
          <router-link
            to="/signup"
            class="text-blue-500 hover:underline text-sm flex items-center gap-1"
          >
            <UIcon name="material-symbols:person-add" class="w-5 h-5" />
            注册账号
          </router-link>
        </div>
        
        <!-- 登录按钮 -->
        <div class="flex justify-center">
          <UButton
            class="w-fit"
            icon="material-symbols:login"
            size="xl"
            :loading="loading"
            type="submit"
            @click="onBtnLoginClick"
          >
            登录
          </UButton>
        </div>
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
import socket from '@/utils/socket'


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
    const response = await request.post('/api/auth/login', {
      username: account.value,
      password: password.value
    })
    if (response.data.code === 200) {
      store.commit('SET_USER', response.data.data.user)
      store.commit('SET_TOKEN', response.data.data.token)
      socket.connect(response.data.data.user.id)
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