<script setup>
// @ts-check
import { reactive } from 'vue'
import globals from '../assets/globals'

class FormLogin {
  // 表单值
  values = reactive({
    email: '',
    password: '',
  })
  // 激活状态
  actived = reactive({
    server: !!globals.server,
    email: !!this.values.email,
    password: !!this.values.password,
  })
  // 判断函数
  focusin = reactive({
    server: () => { this.actived.server = true },
    email: () => { this.actived.email = true },
    password: () => { this.actived.password = true },
  })
  focusout = reactive({
    server: () => { if (!globals.server) this.actived.server = false },
    email: () => { if (!this.values.email) this.actived.email = false },
    password: () => { if (!this.values.password) this.actived.password = false },
  })

  submit() {

  }
}

const formL = reactive(new FormLogin())
</script>

<template>
  <form
    class="m-auto w-full h-full flex flex-col bg-login-900 p-8 slab:max-w-md slab:h-auto slab:rounded-md slab:shadow-neutral-800 slab:shadow-md"
    action="/" method="post" onsubmit="return false" @submit="formL.submit">
    <div class="text-login-400 flex justify-center items-center mt-8 mb-16 text-xl slab:mb-8">登录</div>
    <div class="space-y-8 h-full flex flex-col">
      <label class="input-container">
        <select class="input-box" name="" id="server" v-model="globals.server" :title="globals.server.strAddr"
          @focusin="formL.focusin.server" @focusout="formL.focusout.server">
          <option v-for="server in globals.servers" :value="server" :title="server.strAddr">{{ server.name }}
          </option>
        </select>
        <div class="input-title" :data-active="formL.actived.server">连接</div>
      </label>
      <label class="input-container">
        <input class="input-box" type="text" name="" id="email" autocomplete="email" v-model="formL.values.email"
          @focusin="formL.focusin.email" @focusout="formL.focusout.email">
        <div class="input-title" :data-active="formL.actived.email">邮箱</div>
      </label>
      <label class="input-container">
        <input class="input-box" type="password" name="" id="password" autocomplete="current-password"
          v-model="formL.values.password" @focusin="formL.focusin.password" @focusout="formL.focusout.password">
        <div class="input-title" :data-active="formL.actived.password">密码</div>
      </label>
    </div>
    <div class="mt-auto flex justify-center">
      <input class="bg-login-400 w-full py-2 mt-12 mb-4 rounded-md cursor-pointer" type="submit" value="登录">
    </div>
  </form>
</template>

<style lang="postcss" scoped>
.input-container {
  @apply relative flex items-center h-8 border-b-2 border-solid border-neutral-400;
}
.input-box {
  @apply z-10 w-full bg-transparent text-neutral-50;
}

.input-title {
  @apply absolute bottom-0 flex items-center h-full mb-0 transition-all text-neutral-400;
}

.input-title[data-active="true"] {
  @apply mb-6 text-sm text-neutral-300;
}
</style>
