<script lang="ts" setup>
import { reactive, ref, Ref, UnwrapNestedRefs } from 'vue'
import Entry from './Entry.vue'
import { app, user } from '../js/app'
import { S_EMAIL_ERROR, S_PASSWORD_ERROR, S_VERIFICATION_ERROR, S_WAIT_VERIFY } from '../js/status'

const emit = defineEmits(['next'])

const props = defineProps<{
  status: UnwrapNestedRefs<{
    loading: boolean,
  }>,
}>()

const hadUser: Ref<boolean | null> = ref(null)

const needVerification = ref(false)

const mbridgeEmail = reactive({
  id: 'login-email',
  title: '邮箱',
  value: user.email,
  activated: !!user.email,
  isFocus: false,
  isValid: true,
  hintText: '',
  async validate() {
    if (mbridgeEmail.isFocus && mbridgeEmail.isValid) {
      return
    }
    if (!mbridgeEmail.value) {
      mbridgeEmail.isValid = true
      hadUser.value = null
      return
    }
    if (mbridgeEmail.value == 'test') { return }
    if (!/^\d+@\w+\.\w+$/.test(mbridgeEmail.value)) {
      mbridgeEmail.hintText = '邮箱格式错误'
      mbridgeEmail.isValid = false
      return
    }
    mbridgeEmail.isValid = true
    hadUser.value = await app.hadUser(undefined, mbridgeEmail.value)
  },
})

if (mbridgeEmail.value) { mbridgeEmail.validate() }

const mbridgePassword = reactive({
  id: 'login-password',
  type: 'password',
  title: '密码',
  value: user.password,
  activated: !!user.password,
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
  id: 'login-confirmpwd',
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
  id: 'login-veri-code',
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

async function login() {
  mbridgeEmail.validate()
  mbridgePassword.validate()
  if (hadUser.value == false) {
    mbridgeConfirmPwd.validate()
  }

  if (!mbridgeEmail.value) {
    mbridgeEmail.hintText = '请输入邮箱'
    mbridgeEmail.isValid = false
  }
  if (!mbridgePassword.value) {
    mbridgePassword.hintText = '请输入密码'
    mbridgePassword.isValid = false
  }
  if (needVerification.value && !mbridgeVeriCode.value) {
    mbridgeVeriCode.hintText = '请输入验证码'
    mbridgeVeriCode.isValid = false
  }
  if (!mbridgeEmail.isValid || !mbridgePassword.isValid || !mbridgeConfirmPwd.isValid || !mbridgeVeriCode.isValid) {
    return
  }

  props.status.loading = true
  var status = await app.login(mbridgeEmail.value, mbridgePassword.value, mbridgeVeriCode.value)
  
  switch (status) {
    case S_EMAIL_ERROR:
      mbridgeEmail.hintText = '邮箱错误'
      mbridgeEmail.isValid = false
      break
    case S_PASSWORD_ERROR:
      mbridgePassword.hintText = '密码错误'
      mbridgePassword.isValid = false
      break
    case S_WAIT_VERIFY:
      needVerification.value = true
      break
    case S_VERIFICATION_ERROR:
      mbridgeVeriCode.hintText = '验证码错误'
      mbridgeVeriCode.isValid = false
      break
  }
  props.status.loading = false
}
</script>

<template>
  <form onsubmit="return false" autocomplete="off">
    <div class="text-login-400 flex justify-center items-center mt-8 mb-16 text-xl slab:mb-8">登录</div>
    <div class="space-y-8 h-full flex flex-col">
      <Entry :mbridge="mbridgeEmail"></Entry>
      <Entry :mbridge="mbridgePassword"></Entry>
      <Entry v-if="hadUser == false" :mbridge="mbridgeConfirmPwd"></Entry>
      <Entry v-if="needVerification" :mbridge="mbridgeVeriCode"></Entry>
    </div>
    <div class="grid mt-auto mb-4 pt-12">
      <div v-if="hadUser"
        class="justify-self-end text-neutral-300 mb-4 cursor-pointer transition-colors hover:text-green-500"
        @click="() => { user.email = mbridgeEmail.value; emit('next') }">
        忘记密码
      </div>
      <input class="bg-login-400 w-full py-2 rounded-md cursor-pointer" type="submit"
        :value="hadUser == null ? '登录/注册' : hadUser == true ? '登录' : '注册'" @click="login">
    </div>
  </form>
</template>
