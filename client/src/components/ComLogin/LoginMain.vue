<script lang="ts" setup>
import { reactive, ref, Ref, UnwrapNestedRefs } from 'vue'
import Entry from './Entry.vue'
import { app, user } from '../js/app'
import { S_EMAIL_ERROR, S_PASSWORD_ERROR, S_VERIFICATION_ERROR, S_WAIT_VERIFY } from '../js/status'

const emit = defineEmits(['next'])

const hadUser: Ref<boolean | null> = ref(null)

const needVerification = ref(false)

const bridgeEmail = reactive({
  id: 'login-email',
  title: '邮箱',
  value: user.email,
  maxLength: 50,
  activated: !!user.email,
  isFocus: false,
  isValid: true,
  hintText: '',
  async validate() {
    if (bridgeEmail.isFocus && bridgeEmail.isValid) {
      return
    }
    if (!bridgeEmail.value) {
      bridgeEmail.isValid = true
      hadUser.value = null
      return
    }
    if (bridgeEmail.value == 'test') { return }
    if (!/^\d+@\w+\.\w+$/.test(bridgeEmail.value)) {
      bridgeEmail.hintText = '邮箱格式错误'
      bridgeEmail.isValid = false
      return
    }
    bridgeEmail.isValid = true
    hadUser.value = await app.hadUser(undefined, bridgeEmail.value)
  },
})

const bridgePassword = reactive({
  id: 'login-password',
  type: 'password',
  title: '密码',
  maxLength: 32,
  value: user.password,
  activated: !!user.password,
  isFocus: false,
  isValid: true,
  hintText: '',
  async validate() {
    if (bridgePassword.isFocus && bridgePassword.isValid) {
      return
    }
    bridgePassword.isValid = true
    if (!bridgePassword.value) {
      return
    }
    if (bridgePassword.value.length < 4 || bridgePassword.value.length > 32) {
      bridgePassword.hintText = '密码长度应为4-32位'
      bridgePassword.isValid = false
    } else if (!/^[\w `~!@#$%^&*()_+-=\[\]{}|\\;:'",<.>/?]*$/.test(bridgePassword.value)) {
      bridgePassword.hintText = '密码应由数字字母和符号组成'
      bridgePassword.isValid = false
    }
  },
})

const bridgeConfirmPwd = reactive({
  id: 'login-confirmpwd',
  type: 'password',
  title: '确认密码',
  value: '',
  maxLength: 32,
  activated: false,
  isFocus: false,
  isValid: true,
  hintText: '',
  async validate() {
    if (bridgeConfirmPwd.isFocus && bridgeConfirmPwd.isValid) {
      return
    }
    bridgeConfirmPwd.isValid = true
    if (!bridgeConfirmPwd.value) {
      return
    }
    if (bridgeConfirmPwd.value != bridgePassword.value) {
      bridgeConfirmPwd.hintText = '确认密码与密码不一致'
      bridgeConfirmPwd.isValid = false
    }
  },
})

const bridgeVeriCode = reactive({
  id: 'login-veri-code',
  title: '',
  value: '',
  maxLength: 50,
  activated: false,
  isFocus: false,
  isValid: true,
  hintText: '',
  setFocusin() {
    bridgeVeriCode.title = '验证码'
  },
  setDefault() {
    if (!bridgeVeriCode.value) {
      bridgeVeriCode.title = '验证码 (已发送至邮箱)'
    }
  },
})

async function login() {
  bridgeEmail.validate()
  bridgePassword.validate()
  if (hadUser.value == false) {
    bridgeConfirmPwd.validate()
  }

  if (!bridgeEmail.value) {
    bridgeEmail.hintText = '请输入邮箱'
    bridgeEmail.isValid = false
  }
  if (!bridgePassword.value) {
    bridgePassword.hintText = '请输入密码'
    bridgePassword.isValid = false
  }
  if (needVerification.value && !bridgeVeriCode.value) {
    bridgeVeriCode.hintText = '请输入验证码'
    bridgeVeriCode.isValid = false
  }
  if (!bridgeEmail.isValid || !bridgePassword.isValid || !bridgeConfirmPwd.isValid || !bridgeVeriCode.isValid) {
    return
  }

  app.loading = true
  var status = await app.login(bridgeEmail.value, bridgePassword.value, bridgeVeriCode.value)
  switch (status) {
    case S_EMAIL_ERROR:
      bridgeEmail.hintText = '邮箱错误'
      bridgeEmail.isValid = false
      break
    case S_PASSWORD_ERROR:
      bridgePassword.hintText = '密码错误'
      bridgePassword.isValid = false
      break
    case S_WAIT_VERIFY:
      needVerification.value = true
      break
    case S_VERIFICATION_ERROR:
      bridgeVeriCode.hintText = '验证码错误'
      bridgeVeriCode.isValid = false
      break
  }
  app.loading = false
}

if (bridgeEmail.value) { bridgeEmail.validate() }
</script>

<template>
  <form onsubmit="return false" autocomplete="off">
    <div class="text-login-400 flex justify-center items-center mt-8 mb-16 text-xl slab:mb-8">登录</div>
    <div class="space-y-8 h-full flex flex-col">
      <Entry :bridge="bridgeEmail"></Entry>
      <Entry :bridge="bridgePassword"></Entry>
      <Entry v-if="hadUser == false" :bridge="bridgeConfirmPwd"></Entry>
      <Entry v-if="needVerification" :bridge="bridgeVeriCode"></Entry>
    </div>
    <div class="grid mt-auto mb-4 pt-10">
      <div v-if="hadUser"
        class="justify-self-end text-neutral-300 mb-2 cursor-pointer transition-colors hover:text-green-500"
        @click="() => { user.email = bridgeEmail.value; emit('next') }">
        忘记密码
      </div>
      <input class="bg-login-400 w-full py-2 rounded-md cursor-pointer" type="submit"
        :value="hadUser == null ? '登录/注册' : hadUser == true ? '登录' : '注册'" @click="login">
    </div>
  </form>
</template>
