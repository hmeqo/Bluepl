<script setup>
import { app } from '../js/app';
import { user } from '../js/globals';

async function logout() {
  await app.logout()
}
</script>

<template>
  <div class="flex flex-col w-full h-full p-4">
    <div>
      <div>{{ user.name }}</div>
      <div>{{ user.email }}</div>
    </div>
    <div class="flex justify-center shadow-md rounded-lg mt-auto px-4 py-2 cursor-pointer" @click="logout">
      退出登录
    </div>
  </div>
</template>
