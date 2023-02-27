<script lang="ts" setup>
import { reactive, ref } from 'vue';
import LoginMain from './ComLogin/LoginMain.vue'
import ResetPassword from './ComLogin/ResetPassword.vue'

const tabs = [LoginMain, ResetPassword]

const currentTabIndex = ref(0)
</script>

<template>
  <div class="relative flex justify-center w-full h-full items-center">
    <component :is="tabs[currentTabIndex]"
      class="flex flex-col p-8 w-full h-full bg-login-900 overflow-hidden transition-all slab:max-w-md slab:h-auto slab:shadow-neutral-800 slab:rounded-md slab:shadow-md"
      @back="currentTabIndex = 0" @next="currentTabIndex = 1">
    </component>
  </div>
</template>