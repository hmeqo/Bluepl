<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import MainScreen1 from './MainScreen1/Screen.vue'
import MainScreen2 from './MainScreen2/Screen.vue'
import { app } from './js/app'
import { user } from './js/globals'

const currentScreen = ref(1)

app.getUserInfo()
app.getDataAccount()
</script>

<template>
  <div class="flex flex-col w-full h-full box-border overflow-hidden">
    <div class="flex h-full overflow-hidden bg-gray-100">
      <MainScreen1 v-if="currentScreen == 1"></MainScreen1>
      <MainScreen2 v-if="currentScreen == 2"></MainScreen2>
    </div>
    <div class="panels grid grid-cols-2 items-center shrink-0 text-center h-10 bg-white" :data-current="currentScreen">
      <div class="panel-1" @click="() => currentScreen = 1">数据</div>
      <div class="panel-2" @click="() => currentScreen = 2">管理</div>
    </div>
  </div>
</template>

<style scoped>
.panels>* {
  @apply cursor-pointer
}

.panels[data-current="1"]>:nth-child(1),
.panels[data-current="2"]>:nth-child(2) {
  @apply text-login-400
}
</style>
