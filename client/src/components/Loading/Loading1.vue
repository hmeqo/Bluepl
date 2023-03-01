<template>
  <div
    class="flex-full-prompt main justify-center items-center self-center w-full h-full text-white bg-neutral-900 bg-opacity-70">
    <span v-for="i in [1, 2, 3, 4, 5, 6]" :style="'--i: ' + (i / 9 - 0.4) + 's'"
      class="block w-2 h-6 mx-1 bg-blue-100"></span>
  </div>
</template>

<style scoped>
@keyframes loading {
  60% {
    @apply h-6
  }

  100% {
    @apply h-20
  }
}

.main>* {
  animation: 0.6s linear var(--i) infinite alternate loading;
}
</style>
