<script lang="ts" setup>
import { ref } from 'vue';
import MainScreen1 from './MainScreen1/Screen.vue'
import MainScreen2 from './MainScreen2/Screen.vue'
import { app } from './js/app'

const currentTabIndex = ref(0)

const tabs = [MainScreen1, MainScreen2]

app.getUserInfo()
app.getDataAccount()
</script>

<template>
  <div class="flex flex-col w-full h-full box-border overflow-hidden slab:flex-row-reverse">
    <div class="flex w-full h-full overflow-hidden bg-gray-100">
      <component :is="tabs[currentTabIndex]"></component>
    </div>
    <div class="panels flex flex-row items-center shrink-0 text-center bg-white slab:flex-col" :data-current="currentTabIndex">
      <div class="w-full px-6 py-2 cursor-pointer slab:px-10 slab:py-4" @click="() => currentTabIndex = 0">数据</div>
      <div class="w-full px-6 py-2 cursor-pointer slab:px-10 slab:py-4" @click="() => currentTabIndex = 1">管理</div>
    </div>
  </div>
</template>

<style scoped>
.panels[data-current="0"]>:nth-child(1),
.panels[data-current="1"]>:nth-child(2) {
  @apply text-login-400
}
</style>
