import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'vant/lib/index.css'
import './styles/tailwind.css'

import { Toast, ImagePreview } from 'vant'

const app = createApp(App)

app.use(router)
app.use(Toast)
app.use(ImagePreview)

app.mount('#app')
