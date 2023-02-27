<script lang="ts" setup>
import { ref, watch, computed } from 'vue';
import { app } from '../js/app';

const emit = defineEmits(['update:model-value'])

const props = defineProps<{
  modelValue: string,
  horizontal?: boolean,
}>()

const refTextarea = ref(null)

// 自动调整 textarea 的大小
function textareaSizeAdapt() {
  var elem: any = refTextarea.value
  elem.style.height = '2rem'
  elem.style.height = elem.scrollHeight + 'px'
}

watch(app, () => {
  if (app.currentAccountId != null) {
    setTimeout(textareaSizeAdapt, 10)
  }
})

const value = computed({
  get() {
    return props.modelValue
  },
  set(newValue: string) {
    emit('update:model-value', newValue)
  },
})
</script>

<template>
  <div class="flex items-center w-full" :class="horizontal ? '' : 'flex-col'">
    <div class="px-2 text-lg" :class="horizontal ? '' : ''">
      <slot></slot>
    </div>
    <div class="border-1 p-1 rounded-lg overflow-hidden w-full bg-white">
      <textarea
        class="flex w-full h-10 px-2 p-1 rounded-md whitespace-normal overflow-hidden resize-none transition-colors focus:bg-gray-100"
        ref="refTextarea" @input="textareaSizeAdapt" v-model="value"></textarea>
    </div>
  </div>
</template>

<style scoped>
.border-1 {
  border: solid 1px #8884;
}
</style>
