<script lang="ts">
export default {
  emits: ['close', 'cancel', 'confirm'],
  props: {
    yes: {
      type: String,
      default: '确定'
    },
    no: {
      type: String,
      default: '取消'
    },
    close() {}
  },
  data() { return {} },
}
</script>

<template>
  <div class="relative flex-full-prompt justify-center items-center">
    <div class="container space-y-6 flex flex-col justify-center items-center w-10/12 p-6 pb-4 rounded-2xl bg-white">
      <div>
        <slot></slot>
      </div>
      <div class="space-x-5 flex justify-center items-center w-full">
        <div class="px-4 py-1 rounded-md" style="background-color: hsl(185, 100%, 55%);" @click="$emit('confirm')">{{ yes }}</div>
        <div class="px-4 py-1 rounded-md bg-gray-200" @click="$emit('cancel')">{{ no }}</div>
      </div>
    </div>
    <div class="-z-10 absolute w-full h-full" @click="$emit('close')"></div>
  </div>
</template>

<style scoped>
.container {
  box-shadow: 0 0 24px #0002;
}
</style>
