<script lang="ts" setup>
import { UnwrapNestedRefs } from 'vue'
import Close from '../icons/Close.vue'

var emit = defineEmits(['close', 'cancel', 'confirm'])

const props = defineProps<{
  yes: string,
  no?: string,
  status: UnwrapNestedRefs<{
    opened: boolean,
  }>,
}>()

function confirm() {
  emit('confirm')
  close()
}

function cancel() {
  emit('cancel')
  close()
}

function close() {
  props.status.opened = false
  emit('close')
}
</script>

<template>
  <div class="main z-50 absolute left-0 top-0 flex w-full h-full justify-center items-center bg-neutral-500 bg-opacity-5 transition-all" :data-opened="status.opened"
    :class="status.opened ? 'opacity-100' : 'opacity-0'">
    <div class="relative shadow-2xl flex flex-col justify-center items-center max-w-full px-16 p-8 pb-6 rounded-2xl bg-white">
      <Close class="absolute top-3 right-6" @click="close"></Close>
      <div>
        <slot></slot>
      </div>
      <div class="space-x-5 flex justify-center items-center w-full mt-6">
        <div v-if="no" class="flex justify-start w-full">
          <div class="px-4 py-1 rounded-md bg-gray-200 cursor-pointer" @click="cancel">{{ no }}</div>
        </div>
        <div class="flex justify-end w-full">
          <div class="px-4 py-1 rounded-md cursor-pointer" style="background-color: hsl(195, 100%, 55%);"
            @click="confirm">
            {{ yes }}
          </div>
        </div>
      </div>
    </div>
    <div class="-z-10 absolute w-full h-full" @click="close"></div>
  </div>
</template>

<style scoped>
@keyframes main {
  100% {
    visibility: hidden;
  }
}

.main:not([data-opened="true"]) {
  animation: 0.16s linear forwards main;
}
</style>
