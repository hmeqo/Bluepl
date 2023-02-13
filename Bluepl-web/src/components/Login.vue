<script lang="ts" setup>
import { reactive } from 'vue'
import Prompt from './prompts/YesNo.vue';
import { app } from './js/app';
import { user, servers, webapi } from './js/globals'
import { S_EMAIL_ERROR, S_PASSWORD_ERROR, S_WAIT_VERIFY } from './js/status';

const formL = reactive({
  // 激活状态
  actived: {
    server: !!user.server,
    email: !!user.email,
    password: !!user.password,
    veriCode: !!user.veriCode,
  },

  isFocus: {
    server: false,
    email: false,
    password: false,
    veriCode: false,
  },

  // 判断函数
  focusin: {
    server: () => {
      formL.actived.server = true
      formL.isFocus.server = true
    },
    email: () => {
      formL.actived.email = true
      formL.isFocus.email = true
    },
    password: () => {
      formL.actived.password = true
      formL.isFocus.password = true
    },
    veriCode: () => {
      formL.actived.veriCode = true
      formL.isFocus.veriCode = true
    },
  },

  focusout: {
    server: () => {
      if (!user.server) formL.actived.server = false
      formL.isFocus.server = false
    },
    email: () => {
      if (!user.email) formL.actived.email = false
      formL.isFocus.email = false
      formL.validate.email()
    },
    password: () => {
      if (!user.password) formL.actived.password = false
      formL.isFocus.password = false
      formL.validate.password()
    },
    veriCode: () => {
      if (!user.veriCode) formL.actived.veriCode = false
      formL.isFocus.veriCode = false
    },
  },

  hintText: {
    email: '',
    password: '',
  },

  isValid: {
    email: true,
    password: true,
  },

  validate: {
    email() {
      if (formL.isFocus.email && formL.isValid.email)
        return
      if (user.email.length && !/^\d+@\w+\.\w+|test$/.test(user.email)) {
        formL.hintText.email = '邮箱格式错误'
        formL.isValid.email = false
      } else {
        formL.isValid.email = true
      }
    },
    password() {
      if (formL.isFocus.password && formL.isValid.password)
        return
      if (user.password.length && !/^[\w `~!@#$%^&*()_+-=\[\]{}|\\;:'",<.>/?]*$/.test(user.password)) {
        formL.hintText.password = '密码应由数字字母和符号组成'
        formL.isValid.password = false
      } else {
        formL.isValid.password = true
      }
    },
    all() {
      formL.validate.email()
      formL.validate.password()
    }
  },

  async login() {
    formL.validate.all()
    if (!user.email) {
      formL.hintText.email = '请输入邮箱'
      formL.isValid.email = false
    }
    if (!user.password) {
      formL.hintText.password = '请输入密码'
      formL.isValid.password = false
    } else if (user.password.length < 4 || user.password.length > 32) {
      formL.hintText.password = '密码长度应为4-32位'
      formL.isValid.password = false
    }
    if (!(formL.isValid.email && formL.isValid.password))
      return
    await app.login()
    switch (webapi.status) {
      case S_EMAIL_ERROR:
        formL.hintText.email = '邮箱错误'
        formL.isValid.email = false
      case S_PASSWORD_ERROR:
        formL.hintText.password = '密码错误'
        formL.isValid.password = false
    }
  },
})

const promptStatus = reactive({
  opened: false,
  text: '',
})
</script>

<template>
  <form
    class="flex flex-col m-auto p-8 w-full h-full bg-login-900 slab:max-w-md slab:h-auto slab:rounded-md slab:shadow-neutral-800 slab:shadow-md"
    action="/" method="post" autocomplete="off" onsubmit="return false" @submit="formL.login">
    <div class="text-login-400 flex justify-center items-center mt-8 mb-16 text-xl slab:mb-8">登录</div>
    <div class="space-y-8 h-full flex flex-col">
      <label class="input-container" :data-valid="true">
        <select v-if="servers.length > 1" class="input-box" name="" id="server" v-model="user.server"
          :title="user.server" @focusin="formL.focusin.server" @focusout="formL.focusout.server">
          <option v-for="server in servers" :value="server.strAddr" :title="server.strAddr">{{ server.name }}
          </option>
        </select>
        <select v-else class="input-box" name="" id="" disabled>
          <option v-for="server in servers" :value="server.strAddr">{{ server.name }}</option>
        </select>
        <div class="input-title" :data-active="formL.actived.server">
          <span>连接</span>
        </div>
      </label>
      <label class="input-container" :data-valid="formL.isValid.email">
        <input class="input-box" type="text" name="" id="email" v-model="user.email" @focusin="formL.focusin.email"
          @focusout="formL.focusout.email" @input="formL.validate.email">
        <div class="input-title" :data-active="formL.actived.email">
          <span>邮箱</span>
          <span class="input-hint">{{ formL.hintText.email }}</span>
        </div>
      </label>
      <label class="input-container" :data-valid="formL.isValid.password">
        <input class="input-box" type="password" name="" id="password" autocomplete="off" v-model="user.password"
          @focusin="formL.focusin.password" @focusout="formL.focusout.password" @input="formL.validate.password">
        <div class="input-title" :data-active="formL.actived.password">
          <span>密码</span>
          <span class="input-hint">{{ formL.hintText.password }}</span>
        </div>
      </label>
      <label v-if="webapi.status == S_WAIT_VERIFY" class="input-container" :data-valid="true">
        <input class="input-box" type="text" name="" id="veri-code" v-model="user.veriCode"
          @focusin="formL.focusin.veriCode" @focusout="formL.focusout.veriCode">
        <div class="input-title" :data-active="formL.actived.veriCode">
          <span>验证码</span>
          <span v-if="!formL.actived.veriCode">(已发送至邮箱)</span>
        </div>
      </label>
    </div>
    <div class="mt-auto flex justify-center">
      <input class="bg-login-400 w-full py-2 mt-12 mb-4 rounded-md cursor-pointer" type="submit" value="登录">
    </div>
    <Prompt :status="promptStatus" :yes="'确定'">{{ promptStatus.text }}</Prompt>
  </form>
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
  @apply space-x-2 absolute bottom-0 flex items-center h-full mb-0 transition-all text-neutral-400;
}

.input-title[data-active="true"] {
  @apply mb-6 text-sm text-neutral-300;
}

.input-hint {
  @apply hidden text-sm text-red-500 transition-all;
}
</style>
