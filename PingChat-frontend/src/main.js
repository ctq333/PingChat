import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from '@/router/index.js'
import './assets/main.css'
import ui from '@nuxt/ui/vue-plugin'
import store from './store'

const app = createApp(App)
app.use(router)
app.use(ui)
app.use(store)
app.mount('#app')
