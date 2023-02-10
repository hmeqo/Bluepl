<script lang="ts" setup>
import Login from './components/Login.vue'
import Loading from './components/Loading.vue'
import NotInternetPrompt from './components/prompts/NotInternet.vue'
import AppScreen1 from './components/AppScreen1/Screen.vue'
import AppScreen2 from './components/AppScreen2/Screen.vue'
import { user } from './components/js/globals'
import { app } from './components/js/app'

user.data.accounts = []
app.init()
</script>

<template>
  <div class="relative flex w-screen h-screen bg-primary-900 box-border overflow-hidden">
    <NotInternetPrompt></NotInternetPrompt>
    <Loading v-if="!app.inited || user.loggingIn" :pattern="1"></Loading>
    <Login v-if="!user.logined"></Login>
    <div v-else class="flex flex-col w-full h-full bg-white">
    <!-- <div class="flex flex-col w-full h-full bg-white"> -->
      <div class="flex h-full overflow-hidden">
        <AppScreen1 v-if="app.currentScreen == 1"></AppScreen1>
        <AppScreen2 v-if="app.currentScreen == 2"></AppScreen2>
      </div>
      <div class="panels grid grid-cols-2 items-center shrink-0 text-center h-10 border-t-2 border-gray-100"
        :data-curpanel="app.currentScreen">
        <div class="panel-1" @click="() => app.currentScreen = 1">账号</div>
        <div class="panel-2" @click="() => app.currentScreen = 2">我的</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panels>* {
  @apply cursor-pointer
}

.panels[data-curpanel="1"]>:nth-child(1),
.panels[data-curpanel="2"]>:nth-child(2) {
  @apply text-login-400
}
</style>
