<script lang="ts" setup>
import { ref, watch, computed } from 'vue';
import {app} from '../js/app';

const emit = defineEmits(['update:model-value'])

const props = defineProps<{
  modelValue: string,
  horizontal?: boolean,
}>()

const textareaElem = ref(null)

watch(textareaElem, () => {
  if (!textareaElem.value) { return }
  setTimeout(() => {
    var elem: any = textareaElem.value
    elem.style.height = elem.scrollHeight + 'px'
    elem.oninput = () => {
      elem.style.height = elem.scrollHeight + 'px'
    }
  }, 100)
})

watch(app, () => {
  if (app.currentAccountId == -1) {
    var elem: any = textareaElem.value
    elem.style.height = '2.5rem'
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
  <div class="flex rounded-xl shadow-md" :class="horizontal ? '' : 'flex-col'">
    <div class="flex justify-center items-center p-2 text-lg" :class="horizontal ? '' : 'pb-0'">
      <slot></slot>
    </div>
    <div class="p-2 w-full h-full">
      <textarea class="flex w-full h-10 p-2 shadow-inner rounded-2xl whitespace-normal overflow-visible resize-none"
        ref="textareaElem" v-model="value"></textarea>
    </div>
  </div>
</template>
