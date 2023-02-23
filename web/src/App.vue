<script lang="ts" setup>
import { computed, ref } from 'vue'
import Main from './components/Main.vue'
import Login from './components/Login.vue'
import Loading from './components/Loading/Loading1.vue'
import NotInternetPrompt from './components/prompts/NotInternet.vue'
import { user } from './components/js/globals'
import { app } from './components/js/app'

// for (var i = 0; i < 3; i++) {
//   user.data.accounts.push({
//     id: 1,
//     platform: 'qq',
//     account: '12313123131231',
//     password: '1534u81f38780d398',
//     note: 'idfijfsocdfjkfvjdifjcaipeifowei',
//   })
// }

const tabs = [Login, Main]

const currentTabIndex = computed(() => {
  return user.logined ? 1 : 0
  // return 1
})

app.init()
</script>

<template>
  <div class="grid w-full h-full overflow-hidden">
    <component :is="tabs[currentTabIndex]"></component>
    <Loading v-if="!app.inited || user.loggingIn"></Loading>
    <NotInternetPrompt></NotInternetPrompt>
  </div>
</template>
