<script lang="ts" setup>
import { computed } from 'vue'
import Main from './components/Main.vue'
import Login from './components/Login.vue'
import Loading from './components/Loading/Loading1.vue'
import NotInternetPrompt from './components/prompts/NotInternet.vue'
import { app, user } from './components/js/app'

// for (var i = 1; i <= 6; i++) {
//   user.dataAccount.list.push({
//     id: -i,
//     platform: 'steam',
//     account: '' + -i,
//     password: '1534u81f38780d398',
//     note: 'idfijfsocdfjkfvjdiaiapf,fjvm;jafjcaifasdfasfsdafasdpeifowei',
//   })
// }

const tabs = [Login, Main]

const currentTabIndex = computed(() => {
  // return 1
  return app.logined ? 1 : 0
})

addEventListener('load', async () => {
  await app.init()
})
</script>

<template>
  <div class="flex w-full h-full overflow-hidden bg-primary-900 whitespace-nowrap">
    <component v-if="app.inited" :is="tabs[currentTabIndex]"></component>
    <Loading v-if="app.loading"></Loading>
    <NotInternetPrompt></NotInternetPrompt>
  </div>
</template>
