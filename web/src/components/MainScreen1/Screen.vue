<script lang="ts" setup>
import { ref, computed } from 'vue';
import Account from './Account.vue'
import Detail from './Detail.vue'
import Search from '../icons/Search.vue'
import Add from '../icons/Add.vue'
import { user } from '../js/globals'
import { app } from '../js/app';

const searchFocused = ref(false)

const keyword = ref('')

const accounts = computed(() => {
  var kw = keyword.value
  if (kw) {
    return user.data.accounts.filter(value => {
      if (
        value.platform.indexOf(kw) != -1
        || value.account.indexOf(kw) != -1
        || value.note.indexOf(kw) != -1
      ) {
        return true
      }
      return false
    })
  }
  return user.data.accounts
})
</script>

<template>
  <div class="flex flex-col w-full h-full overflow-hidden">
    <div class="flex justify-center p-4">
      <div class="flex w-full h-full max-w-xs rounded-full shadow-md transition-all bg-white"
        :class="searchFocused ? 'max-w-md' : ''">
        <div class="relative flex items-center w-full h-full px-4 rounded-full">
          <input class="w-full h-full bg-transparent" type="text" name="" id="" autocomplete="off"
            v-model="keyword" @focusin="() => searchFocused = true" @focusout="() => searchFocused = false">
        </div>
        <div class="group flex p-2 rounded-full cursor-pointer">
          <Search></Search>
        </div>
      </div>
      <div class="shrink-0 flex justify-start items-center ml-4 w-8 transition-all"
        :class="searchFocused ? 'w-0 ml-0 opacity-0' : 'opacity-100'">
        <Add class="shrink-0 group" @click="app.createDataAccount"></Add>
      </div>
    </div>
    <div
      class="w-full p-2 overflow-y-auto slab:grid slab:content-start md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
      <div v-for="account in accounts" class="p-2 w-full">
        <Account :account-id="account.id"></Account>
      </div>
    </div>
    <div v-if="!user.data.accounts.length" class="flex justify-center items-center h-full text-neutral-500">
      <div>没有数据</div>
      <Add class="group ml-2" @click="app.createDataAccount"></Add>
    </div>
    <Detail></Detail>
  </div>
</template>
