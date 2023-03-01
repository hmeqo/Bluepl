<script lang="ts" setup>
import { ref, computed, UnwrapNestedRefs } from 'vue'
import Account from './ComUserData/Account.vue'
import Detail from './ComUserData/Detail.vue'
import Search from './icons/Search.vue'
import Add from './icons/Add.vue'
import { app, user } from './js/app'

const props = defineProps<{
  bridge: UnwrapNestedRefs<{
    showUserHome: boolean
  }>
}>()

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
    <div class="z-0 shrink-0 relative flex items-center p-4 box-content">
      <div class="shrink-0 flex justify-start ml-auto transition-all"
        :class="searchFocused ? 'w-0 opacity-0' : 'w-9 opacity-100'">
        <div class="shrink-0 flex">
          <img class="w-8 h-8 object-contain rounded-xl border-2 border-white bg-white shadow-md box-content cursor-pointer"
            :src="user.getAvatar()" alt="" @click="bridge.showUserHome = true">
        </div>
      </div>
      <div class="flex justify-center w-full h-full">
        <div class="z-10 flex w-full h-full max-w-xs rounded-lg bg-white shadow-sm transition-all"
          :class="searchFocused ? 'mx-0 max-w-md' : 'mx-4'">
          <div class="flex p-1 w-full h-full">
            <input class="w-full h-full px-2 rounded-md bg-transparent transition-colors focus:bg-gray-200" type="text"
              name="" id="search" autocomplete="off" v-model="keyword" @focusin="() => searchFocused = true"
              @focusout="() => searchFocused = false">
          </div>
          <div class="group flex p-2 rounded-full cursor-pointer">
            <Search></Search>
          </div>
        </div>
      </div>
      <div class="shrink-0 flex justify-end ml-auto transition-all"
        :class="searchFocused ? 'w-0 opacity-0' : 'w-8 opacity-100'">
        <div class="shrink-0 flex">
          <Add class="group" @click="app.createDataAccount"></Add>
        </div>
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
