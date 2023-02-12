import { createApp } from 'vue'
import App from './App.vue'
import { isMobile } from './components/js/util'
import './index.css'

if (isMobile) {
    addEventListener('load', () => {
        document.querySelector('#app').style.height = document.documentElement.clientHeight + 'px'
    })
}

createApp(App).mount('#app')
