<script lang="ts" setup>
import { ref, watch } from 'vue'
import { webapi } from '../js/app';
import { S_NOT_INTERNET_ERROR } from '../js/status';

watch(webapi, () => {
  if (webapi.status == S_NOT_INTERNET_ERROR) {
    opened.value = true
  }
})

const opened = ref(false)
</script>

<template>
  <div v-if="opened"
    class="flex-full-prompt justify-center items-center text-white bg-neutral-900 bg-opacity-70"
    @click="() => opened = false">网络状态不佳</div>
</template>
