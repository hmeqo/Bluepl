import { createApp } from 'vue'
import App from './App.vue'
import { isMobile } from './components/js/util'
import './index.css'

if (isMobile) {
    // addEventListener('load', () => {
    //     document.querySelector('#app').style.height = document.documentElement.clientHeight + 'px'
    // })
}

addEventListener('dragstart', event => {
    // 禁止图片拖拽
    if (event.target.tagName == "IMG") {
        event.preventDefault()
    }
})

createApp(App).mount('#app')
