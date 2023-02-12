<script lang="ts" setup>
import { ref, watch, reactive, Ref, UnwrapNestedRefs } from 'vue';
import Description from './Description.vue'
import Back from '../icons/Back.vue'
import Save from '../icons/Save.vue'
import Delete from '../icons/Delete.vue'
import YesNoPrompt from '../prompts/YesNo.vue'
import { app, getAccountById, getPlatformUrl } from '../js/app'
import { accountType, webapi } from '../js/globals'
import { S_SUCCESS_200 } from '../js/status'

const hasChange = ref(false)

const yesNoPromptStatus = reactive({ opened: false })

const deletePromptStatus = reactive({ opened: false })

const currentAccount: Ref<accountType> = ref({
  id: -1,
  platform: '',
  account: '',
  password: '',
  note: '',
})

const accountRecord: UnwrapNestedRefs<accountType> = reactive({
  id: -1,
  platform: '',
  account: '',
  password: '',
  note: '',
})

watch(app, () => {
  if (app.currentAccountId != -1) {
    currentAccount.value = getAccountById(app.currentAccountId)
    accountRecord.id = currentAccount.value.id
    accountRecord.platform = currentAccount.value.platform
    accountRecord.account = currentAccount.value.account
    accountRecord.password = currentAccount.value.password
    accountRecord.note = currentAccount.value.note
  }
})

watch(accountRecord, () => {
  for (const name in accountRecord) {
    if (accountRecord[name] != currentAccount.value[name]) {
      hasChange.value = true
      return
    }
  }
  hasChange.value = false
})

function isEmpty() {
  return !accountRecord.platform && !accountRecord.account && !accountRecord.password && !accountRecord.note
}

function back() {
  if (isEmpty()) {
    deleteAccount()
    return
  }
  if (hasChange.value) {
    yesNoPromptStatus.opened = true
  } else {
    close()
  }
}

async function save() {
  await app.updateDataAccount([accountRecord])
  if (webapi.status != S_SUCCESS_200) {
    return
  }
  hasChange.value = false
  currentAccount.value.platform = accountRecord.platform
  currentAccount.value.account = accountRecord.account
  currentAccount.value.password = accountRecord.password
  currentAccount.value.note = accountRecord.note
  close()
}

function close() {
  app.currentAccountId = -1
}

async function deleteAccount() {
  await app.deleteDataAccount([currentAccount.value.id])
  close()
}

async function closeDeletePrompt() {
  deletePromptStatus.opened = false
}

async function checkDeleteAccount() {
  if (isEmpty()) {
    deleteAccount()
    return
  }
  deletePromptStatus.opened = true
}
</script>

<template>
  <div class="absolute left-0 top-0 flex flex-col w-full h-full m-0 rounded-none bg-white">
    <div class="flex pt-4 px-4">
      <div class="flex justify-center items-center">
        <Back @click="back"></Back>
      </div>
      <div class="flex justify-center items-center ml-auto">
        <Save v-if="hasChange" class="mx-8" @click="save"></Save>
      </div>
      <div class="flex justify-center items-center">
        <Delete class="w-8 h-8" @click="checkDeleteAccount"></Delete>
      </div>
    </div>
    <div class="flex items-center shrink-0 shadow-md p-4 border-b-2">
      <img class="w-12 h-12 mx-2 object-contain shrink-0" :src="getPlatformUrl(accountRecord.platform)" alt="">
      <div class="flex w-full h-full ml-4s" :title="accountRecord.platform">
        <Description class="w-full" v-model="accountRecord.platform" :horizontal="true">平台</Description>
      </div>
    </div>
    <div class="space-y-4 p-4 h-full overflow-auto">
      <Description v-model="accountRecord.account">账号</Description>
      <Description v-model="accountRecord.password">密码</Description>
      <Description v-model="accountRecord.note" :multiline="true">备注</Description>
    </div>
    <YesNoPrompt :status="yesNoPromptStatus" :yes="'保存'" :no="'不保存'" @confirm="save" @cancel="close">
      是否保存修改
    </YesNoPrompt>
    <YesNoPrompt :status="deletePromptStatus" :yes="'删除'" @confirm="deleteAccount"
      @close="closeDeletePrompt">
      确认删除
    </YesNoPrompt>
  </div>
</template>
