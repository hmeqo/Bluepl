<script lang="ts" setup>
import { ref } from 'vue'
import { app } from '../js/app'
import { user } from '../js/globals'

const name = ref(user.name || 'uid' + user.uid)

async function logout() {
  await app.logout()
}

async function submitName() {
  if (await app.updateUserInfo(name.value)) {
    user.name = name.value
  } else {
    name.value = user.name
  }
}

async function elemNameKeyDown(event: KeyboardEvent) {
  if (event.key == "Enter") {
    event.target?.blur()
  }
}
</script>

<template>
  <div class="flex flex-col w-full h-full p-4">
    <div class="slab:max-w-sm">
      <div class="flex bg-white p-4 rounded-lg shadow-sm">
        <div class="shrink-0 w-16 h-16 rounded-xl border-gray-100 border-2 border-solid overflow-hidden">
          <img :src="user.avatar || '/useravatar/default.png'" alt="">
        </div>
        <div class="ml-4 flex flex-col w-full overflow-hidden">
          <input ref="elemName" class="overflow-hidden text-ellipsis transition-all rounded-md px-2 py-1 w-full hover:bg-gray-50 focus:bg-gray-100"
            type="text" name="" id="" v-model="name" @focusout="submitName" @keydown="elemNameKeyDown">
        </div>
      </div>
      <div class="flex justify-center shadow-sm rounded-lg px-4 py-2 mt-4 bg-white cursor-pointer" @click="logout">
        退出登录
      </div>
    </div>
  </div>
</template>
