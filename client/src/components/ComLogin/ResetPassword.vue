<script lang="ts" setup>
import { reactive, ref, UnwrapNestedRefs } from 'vue'
import Entry from './Entry.vue'
import Back from '../icons/Back.vue'
import YesNoPrompt from '../prompts/YesNo.vue'
import { app, user } from '../js/app'
import { S_SUCCESS_200, S_VERIFICATION_ERROR, S_WAIT_VERIFY } from '../js/status'

const emit = defineEmits(['back'])

const bridgePassword = reactive({
  id: 'resetpwd-password',
  type: 'password',
  title: '新密码',
  value: '',
  maxLength: 32,
  activated: false,
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
  id: 'resetpwd-confirmpwd',
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
  id: 'resetpwd-vericode',
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

const yesNoPromptStatus = reactive({
  opened: false,
})

const needVerification = ref(false)

const status = ref(0)

async function resetPassword() {
  bridgePassword.validate()
  bridgeConfirmPwd.validate()
  
  if (needVerification.value && !bridgeVeriCode.value) {
    bridgeVeriCode.hintText = '请输入验证码'
    bridgeVeriCode.isValid = false
  }
  if (!bridgePassword.isValid || !bridgeConfirmPwd.isValid || !bridgeVeriCode.isValid) {
    return
  }

  app.loading = true
  status.value = await app.resetPassword(user.email, bridgePassword.value || undefined, bridgeVeriCode.value || undefined)
  app.loading = false
  
  switch (status.value) {
    case S_SUCCESS_200:
      user.password = bridgePassword.value
      yesNoPromptStatus.opened = true
      break
    case S_WAIT_VERIFY:
      needVerification.value = true
      break
    case S_VERIFICATION_ERROR:
      bridgeVeriCode.hintText = '验证码错误'
      bridgeVeriCode.isValid = false
      break
    default:
      yesNoPromptStatus.opened = true
      break
  }
}

function close() {
  if (status.value == S_SUCCESS_200) {
    emit('back')
  }
}
</script>

<template>
  <div class="z-10">
    <div class="flex">
      <Back class="border-neutral-500" @click="() => emit('back')"></Back>
    </div>
    <form class="flex flex-col w-full h-full mt-2" onsubmit="return false">
      <div>
        <div class="mb-16 text-center text-login-400 text-lg slab:mb-8">重置密码</div>
      </div>
      <div>
        <Entry :bridge="bridgePassword"></Entry>
        <Entry class="mt-8" :bridge="bridgeConfirmPwd"></Entry>
        <Entry v-if="needVerification" class="mt-8" :bridge="bridgeVeriCode"></Entry>
      </div>
      <div class="grid mt-auto mb-4 pt-10">
        <input class="bg-login-400 w-full py-2 rounded-md cursor-pointer" type="submit" value="确定" @click="resetPassword">
      </div>
    </form>
    <YesNoPrompt :yes="'确定'" :status="yesNoPromptStatus" @close="close">
      {{ status == S_SUCCESS_200 ? '密码重置成功' : '密码重置失败' }}
    </YesNoPrompt>
  </div>
</template>
