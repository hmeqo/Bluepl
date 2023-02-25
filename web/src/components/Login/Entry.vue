<script lang="ts" setup>
import { UnwrapNestedRefs } from 'vue'

const props = defineProps<{
  mbridge: UnwrapNestedRefs<{
    id?: string,
    type?: string,
    title: string,
    value: string,
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
  props.mbridge.activated = true
  props.mbridge.isFocus = true
  if (props.mbridge.setFocusin) { props.mbridge.setFocusin() }
}

function focusout() {
  if (!props.mbridge.value) { props.mbridge.activated = false }
  props.mbridge.isFocus = false
  if (props.mbridge.setDefault) { props.mbridge.setDefault() }
  validate()
}

function validate() {
  if (props.mbridge.validate) { props.mbridge.validate() }
  else { props.mbridge.isValid = true }
}

if (props.mbridge.setDefault) { props.mbridge.setDefault() }
</script>

<template>
  <label class="input-container" :data-valid="mbridge.isValid">
    <input class="input-box" :type="mbridge.type || 'text'" name="" :id="mbridge.id || ''" v-model="mbridge.value"
      @focusin="focusin" @focusout="focusout" @input="validate"
      :autocomplete="mbridge.type == 'password' ? 'off' : 'new-password'">
    <div class="input-title" :data-active="mbridge.activated">
      <span>{{ mbridge.title }}</span>
      <span class="input-hint">{{ mbridge.hintText }}</span>
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
