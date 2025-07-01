import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// 按照你的views文件结构引入
import Login from '@/views/Login.vue'
import Signup from '@/views/Signup.vue'
import ChatView from '@/views/ChatView.vue'
import UserProfileView from '@/views/UserProfileView.vue'
import AdminView from '@/views/AdminView.vue'
import GroupManageView from '@/views/GroupManageView.vue'
import ExportView from '@/views/ExportView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const routes = [
  { path: '/', redirect: '/chat' },
  { 
    path: '/login', 
    component: Login, 
    name: 'login', 
    meta: { hideNavBar: true } 
  },
  { 
    path: '/signup', 
    component: Signup, 
    name: 'signup', 
    meta: { hideNavBar: true } 
  },
  { 
    path: '/chat', 
    component: ChatView, 
    name: 'chat', 
    meta: { requiresAuth: true, hideNavBar: false } 
  },
  { 
    path: '/profile', 
    component: UserProfileView, 
    name: 'profile', 
    meta: { requiresAuth: true, hideNavBar: false } 
  },
  { 
    path: '/admin', 
    component: AdminView, 
    name: 'admin', 
    meta: { requiresAuth: true, requiresAdmin: true, hideNavBar: false } 
  },
  { 
    path: '/admin/users', 
    component: () => import('@/pages/admin/users.vue'), 
    name: 'admin-users', 
    meta: { requiresAuth: true, requiresAdmin: true, hideNavBar: false } 
  },
  { 
    path: '/admin/online-users', 
    component: () => import('@/pages/admin/online-users.vue'), 
    name: 'admin-online-users', 
    meta: { requiresAuth: true, requiresAdmin: true, hideNavBar: false } 
  },
  { 
    path: '/admin/chat-monitor', 
    component: () => import('@/pages/admin/chat-monitor.vue'), 
    name: 'admin-chat-monitor', 
    meta: { requiresAuth: true, requiresAdmin: true, hideNavBar: false } 
  },
  { 
    path: '/group', 
    component: GroupManageView, 
    name: 'group', 
    meta: { requiresAuth: true, hideNavBar: false } 
  },
  { 
    path: '/export', 
    component: ExportView, 
    name: 'export', 
    meta: { requiresAuth: true, hideNavBar: false } 
  },
  { 
    path: '/:pathMatch(.*)*', 
    component: NotFoundView, 
    name: 'notfound', 
    meta: { hideNavBar: true } 
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫重写
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.meta.requiresAdmin

  // 直接从 localStorage 获取
  const token = localStorage.getItem('token')
  const userJson = localStorage.getItem('user')
  const user = userJson ? JSON.parse(userJson) : null
  const isLogin = !!token && !!user
  const isAdmin = user && user.is_admin

  if (requiresAuth && !isLogin) {
    next('/login')
  } else if (requiresAdmin && !isAdmin) {
    next('/chat')
  } else {
    next()
  }
})

export default router