<script lang="ts" setup>
import { ref } from 'vue';
import MainScreen1 from './MainScreen1/Screen.vue'
import MainScreen2 from './MainScreen2/Screen.vue'
import { isMobile } from './js/util'

const currentTabIndex = ref(0)

const tabs = [MainScreen1, MainScreen2]
const tabLabels = ['数据', '管理']
</script>

<template>
  <div class="main flex flex-col w-full h-full box-border overflow-hidden" :data-ismobile="isMobile">
    <div class="flex w-full h-full overflow-hidden from-gray-100 to-gray-200 bg-gradient-to-br">
      <component :is="tabs[currentTabIndex]"></component>
    </div>
    <div class="panels shrink-0 grid grid-cols-2 justify-items-center content-start p-2 text-center bg-white"
      :data-current="currentTabIndex">
      <div v-for="tabIndex in tabs.keys()" class="z-0 relative w-full py-1 rounded-lg cursor-pointer hover:bg-green-50"
        :data-activated="currentTabIndex == tabIndex" @click="() => currentTabIndex = tabIndex">
        {{ tabLabels[tabIndex] }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.main:not([data-ismobile="true"]) {
  @apply flex-row-reverse;
}

.main:not([data-ismobile="true"]) .panels {
  @apply grid-cols-1;
}

.main:not([data-ismobile="true"]) .panels>* {
  @apply py-3 px-10;
}

.panels>*[data-activated="true"] {
  @apply bg-green-400
}
</style>
