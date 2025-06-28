<template>
  <div class="fixed inset-0 flex items-center justify-center overflow-hidden">
    <div class="w-full max-w-md mx-auto bg-white rounded-2xl shadow-lg px-8 py-10">
      <form @submit.prevent="onRegisterClick" class="space-y-6" autocomplete="off">
        <h2 class="text-3xl font-bold text-center mb-8 flex items-center justify-center gap-2">
          注册
        </h2>
        <!-- 用户名输入框 -->
        <UFormGroup
          class="w-full block"
          :error="inputError && !account ? '请输入用户名' : undefined"
        >
          <UInput
            v-model="account"
            icon="material-symbols:person"
            placeholder="用户名"
            autocomplete="username"
            class="w-full text-xl"
            color="neutral"
            size="xl"
            :ui="{
              base: 'w-full',
              input: (inputError && !account ? 'border-red-500' : 'border-gray-300 focus:border-blue-500') + ' w-full h-14 text-xl px-4'
            }"
          />
        </UFormGroup>
        <!-- 密码输入框 -->
        <UFormGroup
          class="w-full block"
          :error="inputError && !password ? '请输入密码' : undefined"
        >
          <div class="relative w-full">
            <UInput
              v-model="password"
              icon="material-symbols:lock"
              :type="showPassword ? 'text' : 'password'"
              placeholder="密码"
              autocomplete="new-password"
              class="w-full pr-12 text-xl"
              size="xl"
              color="neutral"
              :ui="{
                base: 'w-full',
                input: (inputError && !password ? 'border-red-500' : 'border-gray-300 focus:border-blue-500') + ' w-full h-14 text-xl px-4 pr-12'
              }"
            />
            <!-- 密码显示/隐藏按钮 -->
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500"
              tabindex="-1"
            >
              <UIcon :name="showPassword ? 'material-symbols:visibility-off' : 'material-symbols:visibility'" class="w-6 h-6" />
            </button>
          </div>
        </UFormGroup>
        <!-- 返回登录按钮 -->
        <div class="flex justify-between items-center">
          <router-link
            to="/login"
            class="text-blue-500 hover:underline text-sm flex items-center gap-1"
          >
            <UIcon name="material-symbols:arrow-back" class="w-5 h-5" />
            返回登录
          </router-link>
        </div>
        <!-- 注册按钮 -->
        <div class="flex justify-center">
          <UButton
            class="w-fit px-5 h-12 text-base"
            icon="material-symbols:person-add"
            :loading="loading"
            type="submit"
          >
            注册
          </UButton>
        </div>
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
        router.push('/login')
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