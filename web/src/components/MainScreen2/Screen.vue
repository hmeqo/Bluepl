<script lang="ts" setup>
import { app } from '../js/app';
import { user } from '../js/globals';

async function logout() {
  await app.logout()
}
</script>

<template>
  <div class="space-y-4 flex flex-col w-full h-full p-4">
    <div class="flex bg-white p-4 rounded-lg shadow-sm">
      <div class="shrink-0 w-16 h-16 rounded-xl border-gray-100 border-2 border-solid overflow-hidden">
        <img :src="user.avatar || '/useravatar/default.png'" alt="">
      </div>
      <div class="ml-4 overflow-hidden">
        <div class="flex pt-2">
          <div class="ml-2 overflow-hidden text-ellipsis">{{ user.name || 'uid' + user.uid }}</div>
        </div>
      </div>
    </div>
    <div class="flex justify-center shadow-sm rounded-lg px-4 py-2 bg-white cursor-pointer" @click="logout">
      退出登录
    </div>
  </div>
</template>
