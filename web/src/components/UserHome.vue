<script lang="ts" setup>
import { ref, UnwrapNestedRefs } from 'vue'
import { app, user } from './js/app'
import Back from './icons/Back.vue'
import Close from './icons/Close.vue'

const props = defineProps<{
  bridge: UnwrapNestedRefs<{
    showUserHome: boolean
  }>
}>()

const showFullImg = ref(false)

const name = ref(user.name)

async function logout() {
  await app.logout()
}

async function submitName() {
  if (name.value == user.name) {
    return
  }
  if (await app.updateUserInfo(name.value)) {
    user.name = name.value
  } else {
    name.value = user.name
  }
}

async function elemNameKeyDown(event: KeyboardEvent) {
  if (event.key == "Enter") {
    var elem: any = event.target
    elem?.blur()
  }
}

function close() {
  props.bridge.showUserHome = false
}
</script>

<template>
  <div class="delay-hidden relative flex flex-col w-full h-full p-4 transition-all"
    :class="bridge.showUserHome ? '-left-full slab:opacity-100' : 'left-0 slab:opacity-0 slab:-left-full'"
    :data-hidden="!bridge.showUserHome">
    <div class="flex">
      <div class="flex">
        <Back class="block slab:hidden" @click="close"></Back>
      </div>
      <div class="flex ml-auto">
        <Close class="hidden slab:block" @click="close"></Close>
      </div>
    </div>
    <div class="mt-4 slab:max-w-sm">
      <div class="flex bg-white p-4 rounded-md shadow-sm">
        <div class="shrink-0 w-16 h-16 rounded-lg border-gray-100 border-2 border-solid overflow-hidden">
          <img class="object-contain cursor-pointer"
            :class="showFullImg ? 'absolute left-0 top-0 w-screen h-screen bg-neutral-500 bg-opacity-40' : ''"
            :src="user.getAvatar()" alt="" @click="showFullImg = !showFullImg">
        </div>
        <div class="ml-4 flex flex-col w-full overflow-hidden">
          <input
            class="overflow-hidden text-ellipsis transition-all rounded-md px-2 py-1 w-full hover:bg-gray-50 focus:bg-gray-200"
            type="text" name="" id="" v-model="name" @focusout="submitName" @keydown="elemNameKeyDown">
        </div>
      </div>
      <div class="flex justify-center shadow-sm rounded-md px-4 py-2 mt-4 bg-white cursor-pointer" @click="logout">
        退出登录
      </div>
    </div>
  </div>
</template>
