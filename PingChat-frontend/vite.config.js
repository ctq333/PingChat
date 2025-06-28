import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt/ui/vite'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import Icons from 'unplugin-icons/vite'

export default defineConfig(({ mode }) => {
  // 读取 env 文件
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      vue(),
      ui({
        ui: {
          colors: {
            primary: 'blue',
            neutral: 'zinc'
          }
        }
      }),
      tailwindcss(),
      Icons({
        autoInstall: true,
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
})