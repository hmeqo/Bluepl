<script setup>
import Search from '../img/Search.vue'
import AccountList from './AccountList.vue'
import { user } from '../js/app'
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <div class="p-4">
      <div class="flex w-full h-full rounded-full shadow-md">
        <input class="w-full h-full px-4 rounded-full shadow-inner" type="text" name="" id="" autocomplete="off">
        <div class="flex p-2">
          <Search></Search>
        </div>
      </div>
    </div>
    <div class="space-y-2 overflow-y-auto p-4">
      <AccountList v-for="account in user.data.accounts" :account="account"></AccountList>
    </div>
  </div>
</template>
