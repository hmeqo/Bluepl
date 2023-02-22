<script lang="ts" setup>
import Main from './components/Main.vue'
import Login from './components/Login.vue'
import Loading from './components/Loading/Loading1.vue'
import NotInternetPrompt from './components/prompts/NotInternet.vue'
import { user } from './components/js/globals'
import { app } from './components/js/app'

// for (var i = 0; i < 3; i++) {
//   user.data.accounts.push({
//     id: 1,
//     platform: '',
//     account: '',
//     password: '',
//     note: '',
//   })
// }
app.init()
</script>

<template>
  <div class="dark grid w-full h-full overflow-hidden">
    <Main v-if="user.logined"></Main>
    <Login v-else></Login>
    <Loading v-if="!app.inited || user.loggingIn"></Loading>
    <NotInternetPrompt></NotInternetPrompt>
  </div>
</template>
