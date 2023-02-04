<script lang="ts" setup>
import { reactive } from 'vue'
import { app } from './js/globals'
import { net, servers } from './js/network'

class FormLogin {
  // 激活状态
  actived = reactive({
    server: !!net.user.server,
    email: !!net.user.email,
    password: !!net.user.password,
    veriCode: !!net.user.veriCode,
  })
  // 判断函数
  focusin = reactive({
    server: () => { this.actived.server = true },
    email: () => { this.actived.email = true },
    password: () => { this.actived.password = true },
    veriCode: () => { this.actived.veriCode = true },
  })
  focusout = reactive({
    server: () => { if (!net.user.server) this.actived.server = false },
    email: () => { if (!net.user.email) this.actived.email = false },
    password: () => { if (!net.user.password) this.actived.password = false },
    veriCode: () => { if (!net.user.veriCode) this.actived.veriCode = false },
  })

  async submit() {
    app.status = await net.api.login()
    if (app.status == 200) {
      net.user.logined = true
    }
  }
}

const formL = reactive(new FormLogin())
</script>

<template>
  <form
    v-if="app.status != 200"
    class="m-auto w-full h-full bg-login-900 slab:max-w-md slab:h-auto slab:rounded-md slab:shadow-neutral-800 slab:shadow-md"
    action="/" method="post" onsubmit="return false" @submit="formL.submit">
    <div class="w-full h-full flex flex-col p-8">
      <div class="text-login-400 flex justify-center items-center mt-8 mb-16 text-xl slab:mb-8">登录</div>
      <div class="space-y-8 h-full flex flex-col">
        <label class="input-container">
          <select class="input-box" name="" id="server" v-model="net.user.server" :title="net.user.server"
            @focusin="formL.focusin.server" @focusout="formL.focusout.server">
            <option v-for="server in servers" :value="server.strAddr" :title="server.strAddr">{{ server.name }}
            </option>
          </select>
          <div class="input-title" :data-active="formL.actived.server">连接</div>
        </label>
        <label class="input-container">
          <input class="input-box" type="text" name="" id="email" autocomplete="email" v-model="net.user.email"
            @focusin="formL.focusin.email" @focusout="formL.focusout.email">
          <div class="input-title" :data-active="formL.actived.email">邮箱</div>
        </label>
        <label class="input-container">
          <input class="input-box" type="password" name="" id="password" autocomplete="current-password"
            v-model="net.user.password" @focusin="formL.focusin.password" @focusout="formL.focusout.password">
          <div class="input-title" :data-active="formL.actived.password">密码</div>
        </label>
        <label v-if="app.status == 102" class="input-container">
          <input class="input-box" type="text" name="" id="veri-code" v-model="net.user.veriCode"
            @focusin="formL.focusin.veriCode" @focusout="formL.focusout.veriCode">
          <div class="input-title" :data-active="formL.actived.veriCode">
            验证码
            <span class="ml-1" v-if="!formL.actived.veriCode">(已发送至邮箱)</span>
          </div>
        </label>
      </div>
      <div class="mt-auto flex justify-center">
        <input class="bg-login-400 w-full py-2 mt-12 mb-4 rounded-md cursor-pointer" type="submit" value="登录">
      </div>
    </div>
  </form>
  <div v-else class="text-white">登录成功</div>
</template>

<style scoped>
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
