<script lang="ts">
export default {
  emits: ['update:model-value'],
  props: {
    title: String,
    modelValue: String,
    horizontal: Boolean,
    multiline: Boolean,
  },
  data() { return {} },
  mounted() {
    this.$refs.textarea.style.height = this.$refs.textarea.scrollHeight + 'px'
    this.$refs.textarea.oninput = () => {
      this.$refs.textarea.style.height = this.$refs.textarea.scrollHeight + 'px'
    }
  },
  computed: {
    value: {
      get() {
        return this.modelValue
      },
      set(newValue: string) {
        this.$emit('update:model-value', newValue)
      },
    },
  },
}
</script>

<template>
  <div class="flex rounded-xl shadow-md" :class="horizontal ? '' : 'flex-col'">
    <div class="flex justify-center items-center p-2 text-lg" :class="horizontal ? '' : 'pb-0'">
      <slot></slot>
    </div>
    <div class="p-2 w-full h-full">
      <textarea class="flex w-full h-10 p-2 shadow-inner rounded-2xl whitespace-normal overflow-visible resize-none"
        ref="textarea" v-model="value"></textarea>
    </div>
  </div>
</template>
