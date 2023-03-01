<script lang="ts" setup>
import { reactive, ref } from 'vue'
import UserData from './UserData.vue'
import UserHome from './UserHome.vue'
import { isMobile } from './js/util'

const currentTabIndex = ref(0)
const tabs = [UserData]
const tabLabels = ['数据']

const bridge = reactive({
  showUserHome: false,
})
</script>

<template>
  <div class="main flex flex-col w-full h-full box-border overflow-hidden" :data-ismobile="isMobile">
    <div class="tab-pages flex w-full h-full overflow-hidden">
      <component :is="tabs[currentTabIndex]" :bridge="bridge"></component>
      <UserHome :bridge="bridge"></UserHome>
    </div>
    <div v-if="tabs.length > 1" class="panels shrink-0 grid grid-cols-2 justify-items-center content-start p-2 text-center bg-white"
      :data-current="currentTabIndex">
      <div v-for="tabIndex in tabs.keys()" class="w-full py-1 rounded-lg cursor-pointer hover:bg-green-50"
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
  @apply bg-green-400;
}

.tab-pages>* {
  @apply shrink-0 from-gray-100 to-gray-200 bg-gradient-to-br;
}
</style>
