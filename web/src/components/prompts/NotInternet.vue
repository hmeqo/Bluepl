<script lang="ts" setup>
import { ref } from 'vue'
import { webapi } from '../js/webapi';
import { S_NOT_INTERNET_ERROR } from '../js/status';

const refRoot = ref(null)

webapi.onRequestEnd.push((status: number) => {
  if (status == S_NOT_INTERNET_ERROR) {
    opened.value = true
    setTimeout(() => {
      var elem: any = refRoot.value
      elem.focus()
    }, 50);
  }
})

const opened = ref(false)
</script>

<template>
  <button v-if="opened"
    class="flex-full-prompt justify-center items-center text-white bg-neutral-900 bg-opacity-70 cursor-default"
    @click="() => opened = false" ref="refRoot" tabindex="0">
    网络状态不佳
  </button>
</template>
