<script lang="ts" setup>
import { ref, computed } from 'vue';
import Account from './Account.vue'
import Detail from './Detail.vue'
import Search from '../icons/Search.vue'
import Add from '../icons/Add.vue'
import { app, user } from '../js/app';

const searchFocused = ref(false)

const keyword = ref('')

const accounts = computed(() => {
  var kw = keyword.value.toLowerCase()
  var is_re = false
  if (kw.startsWith('/') && kw.endsWith('/')) {
    is_re = true
    kw = kw.slice(1, length - 1)
  }
  if (kw) {
    return user.dataAccount.list.filter(value => {
      if (is_re) {
        if (
          value.platform.toLowerCase().search(kw) != -1
          || value.account.toLowerCase().search(kw) != -1
          || value.note.toLowerCase().search(kw) != -1
        ) {
          return true
        }
      } else if (
        value.platform.toLowerCase().indexOf(kw) != -1
        || value.account.toLowerCase().indexOf(kw) != -1
        || value.note.toLowerCase().indexOf(kw) != -1
      ) {
        return true
      }
      return false
    })
  }
  return user.dataAccount.list
})
</script>

<template>
  <div class="flex flex-col w-full h-full overflow-hidden">
    <div class="flex justify-center p-4">
      <div class="flex w-full h-full max-w-xs rounded-lg overflow-hidden shadow-sm transition-all bg-white"
        :class="searchFocused ? 'max-w-md' : ''">
        <div class="relative flex items-center p-1 w-full h-full">
          <input class="w-full h-full px-2 rounded-md bg-transparent focus:bg-gray-200" type="text" name="" id=""
            autocomplete="off" v-model="keyword" @focusin="() => searchFocused = true"
            @focusout="() => searchFocused = false">
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
    <div v-if="user.dataAccount.list.length"
      class="w-full h-full p-2 overflow-y-auto slab:grid slab:content-start sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
      <div v-for="account in accounts" class="grid p-2">
        <Account :account="account"></Account>
      </div>
    </div>
    <div v-else class="flex justify-center items-center h-full text-neutral-500">
      <div>没有数据</div>
      <Add class="group ml-2" @click="app.createDataAccount"></Add>
    </div>
    <Detail></Detail>
  </div>
</template>
