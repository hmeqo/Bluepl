<script lang="ts" setup>
import { reactive, ref, UnwrapNestedRefs } from 'vue'
import Entry from './Entry.vue'
import Back from '../icons/Back.vue'
import YesNoPrompt from '../prompts/YesNo.vue'
import { app, user } from '../js/app'
import { S_NOT_INTERNET_ERROR, S_PASSWORD_ERROR, S_SUCCESS_200, S_VERIFICATION_ERROR, S_WAIT_VERIFY } from '../js/status'

const emit = defineEmits(['back'])

const props = defineProps<{
  status: UnwrapNestedRefs<{
    loading: boolean,
  }>,
}>()

const mbridgePassword = reactive({
  id: 'resetpwd-password',
  type: 'password',
  title: '新密码',
  value: '',
  activated: false,
  isFocus: false,
  isValid: true,
  hintText: '',
  async validate() {
    if (mbridgePassword.isFocus && mbridgePassword.isValid) {
      return
    }
    mbridgePassword.isValid = true
    if (!mbridgePassword.value) {
      return
    }
    if (mbridgePassword.value.length < 4 || mbridgePassword.value.length > 32) {
      mbridgePassword.hintText = '密码长度应为4-32位'
      mbridgePassword.isValid = false
    } else if (!/^[\w `~!@#$%^&*()_+-=\[\]{}|\\;:'",<.>/?]*$/.test(mbridgePassword.value)) {
      mbridgePassword.hintText = '密码应由数字字母和符号组成'
      mbridgePassword.isValid = false
    }
  },
})

const mbridgeConfirmPwd = reactive({
  id: 'resetpwd-confirmpwd',
  type: 'password',
  title: '确认密码',
  value: '',
  activated: false,
  isFocus: false,
  isValid: true,
  hintText: '',
  async validate() {
    if (mbridgeConfirmPwd.isFocus && mbridgeConfirmPwd.isValid) {
      return
    }
    mbridgeConfirmPwd.isValid = true
    if (!mbridgeConfirmPwd.value) {
      return
    }
    if (mbridgeConfirmPwd.value != mbridgePassword.value) {
      mbridgeConfirmPwd.hintText = '确认密码与密码不一致'
      mbridgeConfirmPwd.isValid = false
    }
  },
})

const mbridgeVeriCode = reactive({
  id: 'resetpwd-vericode',
  title: '',
  value: '',
  activated: false,
  isFocus: false,
  isValid: true,
  hintText: '',
  setFocusin() {
    mbridgeVeriCode.title = '验证码'
  },
  setDefault() {
    if (!mbridgeVeriCode.value) {
      mbridgeVeriCode.title = '验证码 (已发送至邮箱)'
    }
  },
})

const yesNoPromptStatus = reactive({
  opened: false,
})

const needVerification = ref(false)

const status = ref(0)

async function resetPassword() {
  mbridgePassword.validate()
  mbridgeConfirmPwd.validate()
  
  if (needVerification.value && !mbridgeVeriCode.value) {
    mbridgeVeriCode.hintText = '请输入验证码'
    mbridgeVeriCode.isValid = false
  }
  if (!mbridgePassword.isValid || !mbridgeConfirmPwd.isValid || !mbridgeVeriCode.isValid) {
    return
  }

  props.status.loading = true
  status.value = await app.resetPassword(user.email, mbridgePassword.value || undefined, mbridgeVeriCode.value || undefined)
  props.status.loading = false
  
  switch (status.value) {
    case S_SUCCESS_200:
      user.password = mbridgePassword.value
      yesNoPromptStatus.opened = true
      break
    case S_WAIT_VERIFY:
      needVerification.value = true
      break
    case S_VERIFICATION_ERROR:
      mbridgeVeriCode.hintText = '验证码错误'
      mbridgeVeriCode.isValid = false
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
        <Entry :mbridge="mbridgePassword"></Entry>
        <Entry class="mt-8" :mbridge="mbridgeConfirmPwd"></Entry>
        <Entry v-if="needVerification" class="mt-8" :mbridge="mbridgeVeriCode"></Entry>
      </div>
      <div class="grid mt-auto mb-4 pt-12">
        <input class="bg-login-400 w-full py-2 rounded-md cursor-pointer" type="submit" value="确定" @click="resetPassword">
      </div>
    </form>
    <YesNoPrompt :yes="'确定'" :status="yesNoPromptStatus" @close="close">
      {{ status == S_SUCCESS_200 ? '密码重置成功' : '密码重置失败' }}
    </YesNoPrompt>
  </div>
</template>
