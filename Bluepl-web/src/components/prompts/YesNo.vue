<script setup>
var emit = defineEmits(['close', 'cancel', 'confirm'])

var props = defineProps({
  yes: {
    type: String,
    default: '确定'
  },
  no: {
    type: String,
    default: ''
  },
})

function confirm() {
  emit('confirm')
  emit('close')
}

function cancel() {
  emit('cancel')
  emit('close')
}

function close() {
  emit('close')
}
</script>

<template>
  <div class="relative flex-full-prompt justify-center items-center bg-neutral-500 bg-opacity-5">
    <div class="shadow-2xl space-y-6 flex flex-col justify-center items-center w-10/12 p-8 pb-6 rounded-2xl bg-white">
      <div>
        <slot></slot>
      </div>
      <div class="space-x-5 flex justify-center items-center w-full">
        <div class="flex justify-end w-full">
          <div class="px-4 py-1 rounded-md cursor-pointer" style="background-color: hsl(195, 100%, 55%);" @click="confirm">
            {{ yes }}
          </div>
        </div>
        <div v-if="no" class="flex justify-start w-full">
          <div class="px-4 py-1 rounded-md bg-gray-200 cursor-pointer" @click="cancel">{{ no }}</div>
        </div>
      </div>
    </div>
    <div class="-z-10 absolute w-full h-full" @click="close"></div>
  </div>
</template>
