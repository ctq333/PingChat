import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from '@/router/index.js'
import './assets/main.css'
import ui from '@nuxt/ui/vue-plugin'
import store from './store'
import socket from '@/utils/socket'


const app = createApp(App)
app.use(router)
app.use(ui)
app.use(store)

const user = JSON.parse(localStorage.getItem('user') || '{}')
if (user && user.id) {
  socket.connect(user.id)
}

app.mount('#app')
