<script lang="ts" setup>
const props = defineProps<{
  pattern: number,
}>()
</script>

<template>
  <div class="z-50 absolute top-0 left-0 w-full h-full grid">
    <div v-if="props.pattern == 1" class="loading-1 w-full h-full flex justify-center items-center self-center text-white bg-neutral-900 bg-opacity-70">
      <span v-for="i in [1, 2, 3, 4, 5, 6]" :style="'--i: ' + (i/9 - 0.4) + 's'" class="block w-2 h-6 mx-1 bg-blue-100"></span>
    </div>
  </div>
</template>

<style scoped>
@keyframes loading-1 {
  60% {
    @apply h-6
  }

  100% {
    @apply h-20
  }
}

.loading-1>* {
  animation: 0.6s linear var(--i) infinite alternate loading-1;
}
</style>
