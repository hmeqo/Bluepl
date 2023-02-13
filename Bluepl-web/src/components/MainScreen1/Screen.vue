<script lang="ts" setup>
import { ref } from 'vue';
import Account from './Account.vue'
import Detail from './Detail.vue'
import Search from '../icons/Search.vue'
import Add from '../icons/Add.vue'
import { user } from '../js/globals'
import { app } from '../js/app';

const searchFocused = ref(false)
</script>

<template>
  <div class="flex flex-col w-full h-full overflow-hidden">
    <div class="flex p-4">
      <div class="searchbar shrink-0 flex w-full h-full rounded-full shadow-md transition-all bg-white"
        :style="searchFocused ? '' : 'width: calc(100% - 3rem)'">
        <input class="w-full h-full px-4 rounded-full shadow-inner" type="text" name="" id="" autocomplete="off"
          @focusin="() => searchFocused = true" @focusout="() => searchFocused = false">
        <div class="group flex p-2 cursor-pointer">
          <Search></Search>
        </div>
      </div>
      <div class="shrink-0 flex justify-start items-center ml-4 w-0">
        <Add class="shrink-0 group w-8 h-8" @click="app.createDataAccount"></Add>
      </div>
    </div>
    <div class="space-y-4 overflow-y-auto p-4">
      <Account v-for="account in user.data.accounts" :account-id="account.id"></Account>
    </div>
    <div v-if="!user.data.accounts.length" class="flex justify-center items-center h-full text-neutral-500">
      <div>没有数据</div>
      <Add class="group ml-2 w-8 h-8" @click="app.createDataAccount"></Add>
    </div>
    <Detail class="con-detail transition-all duration-300" :class="app.currentAccountId == -1 ? 'left-full opacity-0' : 'left-0 opacity-100'" :data-opened="app.currentAccountId != -1"></Detail>
  </div>
</template>

<style scoped>
@keyframes con-detail {
  100% {
    visibility: hidden;
  }
}

.con-detail:not([data-opened="true"]) {
  animation: 0.3s linear forwards con-detail;
}
</style>
