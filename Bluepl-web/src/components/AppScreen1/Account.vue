<script lang="ts" setup>
import { ref, reactive, watch } from 'vue'
import Description from './Description.vue'
import Back from '../icons/Back.vue'
import Save from '../icons/Save.vue'
import Delete from '../icons/Delete.vue'
import YesNoPrompt from '../prompts/YesNo.vue'
import { app } from '../js/app'
import { user, webapi } from '../js/globals'
import { S_SUCCESS_200 } from '../js/status'

const props = defineProps<{
  account: {
    id: number,
    platform: string,
    account: string,
    password: string,
    note: string,
  },
  opened?: boolean,
}>()

const detailOpened = ref(props.opened)

const yesNoPromptOpened = ref(false)

const hasChange = ref(false)

const accountRecord = reactive({
  id: props.account.id,
  platform: props.account.platform,
  account: props.account.account,
  password: props.account.password,
  note: props.account.note,
})

watch(accountRecord, checkChange)

function checkChange() {
  for (const name in accountRecord) {
    if (props.account[name] != accountRecord[name]) {
      hasChange.value = true
      return
    }
  }
  hasChange.value = false
}

function show() {
  detailOpened.value = true
  accountRecord.platform = props.account.platform
  accountRecord.account = props.account.account
  accountRecord.password = props.account.password
  accountRecord.note = props.account.note
}

function back() {
  if (hasChange.value) {
    yesNoPromptOpened.value = true
  } else {
    detailOpened.value = false
  }
}

async function save() {
  await app.updateDataAccount([accountRecord])
  if (webapi.status != S_SUCCESS_200) {
    return
  }
  hasChange.value = false
  props.account.platform = accountRecord.platform
  props.account.account = accountRecord.account
  props.account.password = accountRecord.password
  props.account.note = accountRecord.note
}

async function deleteAccount() {
  await app.deleteDataAccount([props.account.id])
  close(true)
}

function close(closeDetail?: boolean) {
  if (closeDetail) {
    detailOpened.value = false
  }
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
  <div class="rounded-2xl shadow-md overflow-hidden">
    <div class="group main flex p-3 transition-colors cursor-pointer hover:bg-blue-500 bg-opacity-50" @click="show">
      <div class="shrink-0">
        <img class="w-12 h-12 mx-4 object-contain" :src="user.data.platformToImgUrl[account.platform]" alt="">
        <div class="mt-1 text-sm text-center transition-colors group-hover:text-white" :title="account.platform">{{
          account.platform
        }}</div>
      </div>
      <div class="space-y-1 w-full h-full ml-3">
        <div class="text-lg transition-colors group-hover:text-white" :title="account.account">{{ account.account }}
        </div>
        <div class="text-neutral-600 transition-colors group-hover:text-neutral-200" :title="account.note">{{
          account.note
        }}</div>
      </div>
    </div>
    <div v-if="detailOpened" class="absolute left-0 top-0 flex flex-col w-full h-full m-0 rounded-none bg-white">
      <div class="flex p-1 px-3">
        <div class="flex justify-center items-center">
          <Back @click="back"></Back>
        </div>
        <div class="flex justify-center items-center ml-auto">
          <Save v-if="hasChange" class="mx-8" @click="save"></Save>
        </div>
        <div class="flex justify-center items-center">
          <Delete class="w-8 h-8" @click="deleteAccount"></Delete>
        </div>
      </div>
      <div class="flex items-center shrink-0 shadow-md p-4 border-b-2">
        <img class="w-12 h-12 mx-2 object-contain shrink-0" :src="user.data.platformToImgUrl[account.platform]" alt="">
        <div class="flex w-full h-full ml-4s" :title="account.platform">
          <Description class="w-full" v-model="accountRecord.platform" :horizontal="true">平台</Description>
        </div>
      </div>
      <div class="h-full overflow-auto">
        <Description v-model="accountRecord.account">账号</Description>
        <Description v-model="accountRecord.password">密码</Description>
        <Description v-model="accountRecord.note" :multiline="true">描述</Description>
      </div>
      <YesNoPrompt v-if="yesNoPromptOpened" :yes="'保存'" :no="'不保存'" @confirm="save" @close="close">是否保存修改</YesNoPrompt>
    </div>
  </div>
</template>

<style scoped>
.main * {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
