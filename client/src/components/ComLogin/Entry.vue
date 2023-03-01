<script lang="ts" setup>
import { UnwrapNestedRefs } from 'vue'

const props = defineProps<{
  bridge: UnwrapNestedRefs<{
    id?: string,
    type?: string,
    title: string,
    value: string,
    maxLength?: number,
    activated: boolean,
    isFocus: boolean,
    isValid: boolean,
    hintText: string,
    setFocusin?: Function,
    setDefault?: Function,
    validate?: Function,
  }>,
}>()

function focusin() {
  props.bridge.activated = true
  props.bridge.isFocus = true
  if (props.bridge.setFocusin) { props.bridge.setFocusin() }
}

function focusout() {
  if (!props.bridge.value) { props.bridge.activated = false }
  props.bridge.isFocus = false
  if (props.bridge.setDefault) { props.bridge.setDefault() }
  validate()
}

function validate() {
  if (props.bridge.validate) { props.bridge.validate() }
  else { props.bridge.isValid = true }
}

if (props.bridge.setDefault) { props.bridge.setDefault() }
</script>

<template>
  <label class="input-container" :data-valid="bridge.isValid">
    <input class="input-box" :type="bridge.type || 'text'" name="" :id="bridge.id || ''" v-model="bridge.value"
      @focusin="focusin" @focusout="focusout" @input="validate"
      :autocomplete="bridge.type == 'password' ? 'off' : 'new-password'" :maxlength="bridge.maxLength">
    <div class="input-title" :data-active="bridge.activated">
      <span>{{ bridge.title }}</span>
      <span class="input-hint">{{ bridge.hintText }}</span>
    </div>
  </label>
</template>

<style scoped>
@keyframes hint {
  0% {
    background-color: transparent;
  }

  50% {
    background-color: #f009;
  }
}

@keyframes verify-container {
  0% {
    background-color: transparent;
  }

  50% {
    background-color: #8888;
  }
}

.input-container {
  @apply relative flex items-center h-8 border-b-2 border-solid border-neutral-400;
}

.input-container:not([data-valid="true"]) {
  animation: 0.8s ease-out alternate hint;
}

.input-container:not([data-valid="true"]) .input-hint {
  @apply block
}

.input-box {
  @apply z-10 w-full bg-transparent text-neutral-50;
}

.input-title {
  @apply z-0 space-x-2 absolute bottom-0 flex items-center h-full mb-0 transition-all text-neutral-400;
}

.input-title[data-active="true"] {
  @apply mb-6 text-sm text-neutral-300;
}

.input-hint {
  @apply hidden text-sm text-red-500 transition-all;
}
</style>
