<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { app } from './js/app';
import { user, servers } from './js/globals'
import { S_EMAIL_ERROR, S_PASSWORD_ERROR, S_USER_ALREADY_EXISTS, S_WAIT_VERIFY } from './js/status';

const formL = reactive({
  value: {
    password: '',
    confirmPassword: '',
    veriCode: '',
  },

  // 激活状态
  actived: {
    server: !!user.server,
    email: !!user.email,
    password: false,
    confirmPassword: false,
    veriCode: false,
  },

  isFocus: {
    server: false,
    email: false,
    password: false,
    confirmPassword: false,
    veriCode: false,
  },

  hintText: {
    email: '',
    password: '',
    confirmPassword: '',
  },

  isValid: {
    email: true,
    password: true,
    confirmPassword: true,
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
    confirmPassword: () => {
      formL.actived.confirmPassword = true
      formL.isFocus.confirmPassword = true
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
      if (!formL.value.password) formL.actived.password = false
      formL.isFocus.password = false
      formL.validate.password()
    },
    confirmPassword: () => {
      if (!formL.value.confirmPassword) formL.actived.confirmPassword = false
      formL.isFocus.confirmPassword = false
      formL.validate.confirmPassword()
    },
    veriCode: () => {
      if (!formL.value.veriCode) formL.actived.veriCode = false
      formL.isFocus.veriCode = false
    },
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
      app.hadUser(undefined, user.email).then(flag => {
        if (flag) {
          needConfirmPassword.value = false
        } else {
          needConfirmPassword.value = true
        }
      })
    },
    password() {
      if (formL.isFocus.password && formL.isValid.password)
        return
      if (formL.value.password.length && !/^[\w `~!@#$%^&*()_+-=\[\]{}|\\;:'",<.>/?]*$/.test(formL.value.password)) {
        formL.hintText.password = '密码应由数字字母和符号组成'
        formL.isValid.password = false
      } else {
        formL.isValid.password = true
      }
    },
    confirmPassword() {
      if (formL.isFocus.confirmPassword && formL.isValid.confirmPassword)
        return
      if (formL.value.confirmPassword.length && formL.value.confirmPassword != formL.value.password) {
        formL.hintText.confirmPassword = '确认密码与密码不一致'
        formL.isValid.confirmPassword = false
      } else {
        formL.isValid.confirmPassword = true
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
    if (!formL.value.password) {
      formL.hintText.password = '请输入密码'
      formL.isValid.password = false
    } else if (formL.value.password.length < 4 || formL.value.password.length > 32) {
      formL.hintText.password = '密码长度应为4-32位'
      formL.isValid.password = false
    }
    if (!(formL.isValid.email && formL.isValid.password)) {
      return
    }
    if (needConfirmPassword.value && !formL.isValid.confirmPassword) {
      return
    }
    if (awaitVerify.value && !formL.value.veriCode) {
      return
    }
    switch (await app.login(user.email, formL.value.password, formL.value.veriCode)) {
      case S_EMAIL_ERROR:
        formL.hintText.email = '邮箱错误'
        formL.isValid.email = false
        break
      case S_PASSWORD_ERROR:
        formL.hintText.password = '密码错误'
        formL.isValid.password = false
        break
      case S_WAIT_VERIFY:
        awaitVerify.value = true
        break
      default:
        awaitVerify.value = false
        break
    }
  },
})

const needConfirmPassword = ref(false)

const awaitVerify = ref(false)
</script>

<template>
  <form
    class="flex flex-col m-auto p-8 w-full h-full bg-login-900 slab:max-w-md slab:h-auto slab:rounded-md slab:shadow-neutral-800 slab:shadow-md"
    action="/" method="post" autocomplete="off" onsubmit="return false">
    <div class="text-login-400 flex justify-center items-center mt-8 mb-16 text-xl slab:mb-8">登录</div>
    <div class="space-y-8 h-full flex flex-col">
      <label style="display: none;" class="input-container" :data-valid="true">
        <select v-if="servers.length > 1" class="input-box" name="" id="server" v-model="user.server" :title="user.server"
          @focusin="formL.focusin.server" @focusout="formL.focusout.server">
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
        <input class="input-box" type="text" name="" id="email" autocomplete="off" v-model="user.email" @focusin="formL.focusin.email"
          @focusout="formL.focusout.email" @input="formL.validate.email" @keydown="">
        <div class="input-title" :data-active="formL.actived.email">
          <span>邮箱</span>
          <span class="input-hint">{{ formL.hintText.email }}</span>
        </div>
      </label>
      <label class="input-container" :data-valid="formL.isValid.password">
        <input class="input-box" type="password" name="" id="password" autocomplete="off" v-model="formL.value.password"
          @focusin="formL.focusin.password" @focusout="formL.focusout.password" @input="formL.validate.password">
        <div class="input-title" :data-active="formL.actived.password">
          <span>密码</span>
          <span class="input-hint">{{ formL.hintText.password }}</span>
        </div>
      </label>
      <label v-if="needConfirmPassword" class="input-container"
        :data-valid="formL.isValid.confirmPassword">
        <input class="input-box" type="password" name="" id="confirmPassword" autocomplete="off"
          v-model="formL.value.confirmPassword" @focusin="formL.focusin.confirmPassword"
          @focusout="formL.focusout.confirmPassword" @input="formL.validate.confirmPassword">
        <div class="input-title" :data-active="formL.actived.confirmPassword">
          <span>确认密码</span>
          <span class="input-hint">{{ formL.hintText.confirmPassword }}</span>
        </div>
      </label>
      <label v-if="awaitVerify" class="input-container" :data-valid="true">
        <input class="input-box" type="text" name="" id="veri-code" v-model="formL.value.veriCode"
          @focusin="formL.focusin.veriCode" @focusout="formL.focusout.veriCode">
        <div class="input-title" :data-active="formL.actived.veriCode">
          <span>验证码</span>
          <span v-if="!formL.actived.veriCode">(已发送至邮箱)</span>
        </div>
      </label>
    </div>
    <div class="mt-auto flex justify-center">
      <input class="bg-login-400 w-full py-2 mt-12 mb-4 rounded-md cursor-pointer" type="submit" value="登录"
        @click="formL.login">
    </div>
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
  @apply space-x-2 absolute bottom-0 flex items-center h-full mb-0 transition-all text-neutral-400;
}

.input-title[data-active="true"] {
  @apply mb-6 text-sm text-neutral-300;
}

.input-hint {
  @apply hidden text-sm text-red-500 transition-all;
}

.appear-container {
  animation: 0.8s ease-out alternate verify-container;
}</style>
