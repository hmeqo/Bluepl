<script lang="ts" setup>
import { ref, reactive, watch } from 'vue'
import Description from './Description.vue'
import Back from '../img/Back.vue'
import YesNoPrompt from '../prompts/YesNo.vue'
import { user } from '../js/app'

const detailOpened = ref(false)

const yesNoPromptOpened = ref(false)

const hasChange = ref(false)

const props = defineProps<{
  account: {
    id: number,
    platform: string,
    account: string,
    password: string,
    note: string,
  },
}>()

const newAccount = reactive({
  platform: props.account.platform,
  account: props.account.account,
  password: props.account.password,
  note: props.account.note,
})

watch(newAccount, checkChange)

function checkChange() {
  for (const name in newAccount) {
    if (props.account[name] != newAccount[name]) {
      hasChange.value = true
      return
    }
  }
  hasChange.value = false
}

function show() {
  detailOpened.value = true
  newAccount.platform = props.account.platform
  newAccount.account = props.account.account
  newAccount.password = props.account.password
  newAccount.note = props.account.note
}

function back() {
  if (hasChange.value) {
    yesNoPromptOpened.value = true
  } else {
    detailOpened.value = false
  }
}

function save() {
  props.account.platform = newAccount.platform
  props.account.account = newAccount.account
  props.account.password = newAccount.password
  props.account.note = newAccount.note
  user.data.save(newAccount)
  hasChange.value = false
}

function confirm() {
  save()
  cancel()
}

function cancel() {
  close()
  detailOpened.value = false
}

function close() {
  yesNoPromptOpened.value = false
}

onkeydown = (event) => {
  if (event.code == 'Escape') {
    if (yesNoPromptOpened.value) {
      close()
    }
  }
}
</script>

<template>
  <div class="rounded-2xl shadow-md">
    <div class="container flex p-3" @click="show">
      <div class="shrink-0">
        <img class="w-12 h-12 mx-4 object-contain" :src="user.data.platformToImgUrl[account.platform]" alt="">
        <div class="mt-1 text-sm text-center" :title="account.platform">{{ account.platform }}</div>
      </div>
      <div class="space-y-1 w-full h-full ml-3">
        <div class="text-lg" :title="account.account">{{ account.account }}</div>
        <div class="text-neutral-600" :title="account.note">{{ account.note }}</div>
      </div>
    </div>
    <div v-if="detailOpened" class="absolute left-0 top-0 flex flex-col w-full h-full m-0 rounded-none bg-white">
      <div class="shrink-0 p-1 px-3">
        <Back @click="back"></Back>
      </div>
      <div class="flex items-center shrink-0 shadow-md p-4 border-b-2">
        <img class="w-12 h-12 mx-2 object-contain flex-shrink-0" :src="user.data.platformToImgUrl[account.platform]"
          alt="">
        <div class="flex w-full h-full ml-4s" :title="account.platform">
          <Description class="w-full" v-model="newAccount.platform" :horizontal="true">平台</Description>
        </div>
      </div>
      <div class="h-full overflow-auto">
        <Description v-model="newAccount.account">账号</Description>
        <Description v-model="newAccount.password">密码</Description>
        <Description v-model="newAccount.note" :multiline="true">描述</Description>
      </div>
      <YesNoPrompt v-if="yesNoPromptOpened" :yes="'保存'" :no="'不保存'" @close="close" @cancel="cancel" @confirm="confirm">
        是否保存修改
      </YesNoPrompt>
    </div>
  </div>
</template>

<style scoped>
.container * {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
