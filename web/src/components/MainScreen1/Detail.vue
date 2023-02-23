<script lang="ts" setup>
import { ref, watch, reactive, Ref, UnwrapNestedRefs } from 'vue';
import Description from './Description.vue'
import Back from '../icons/Back.vue'
import Save from '../icons/Save.vue'
import Close from '../icons/Close.vue'
import YesNoPrompt from '../prompts/YesNo.vue'
import { app, getAccountById, getPlatformUrl } from '../js/app'
import { accountType } from '../js/globals'
import { isMobile } from '../js/util'

const hasChange = ref(false)

const elemDescription = ref(null)

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
    if (elemDescription.value == null) {return}
    var elem: Element = elemDescription.value
    elem.scrollTo(0, 0)
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

async function save(close_flag?: boolean) {
  var success = await app.updateDataAccount([accountRecord])
  if (!success) {
    return
  }
  hasChange.value = false
  currentAccount.value = getAccountById(app.currentAccountId)
  currentAccount.value.platform = accountRecord.platform
  currentAccount.value.account = accountRecord.account
  currentAccount.value.password = accountRecord.password
  currentAccount.value.note = accountRecord.note
  if (close_flag) {
    close()
  }
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
  <div class="com-detail absolute top-0 grid justify-center items-center w-full h-full transition-all duration-300"
    :class="app.currentAccountId != -1 ? 'left-0 opacity-100' : 'left-full opacity-0 slab:left-0'"
    :data-opened="app.currentAccountId != -1">
    <div class="z-10 flex flex-col w-full h-full bg-white overflow-hidden shadow-xl slab:h-4/6 slab:rounded-lg">
      <div class="flex pt-4 px-4">
        <div class="flex justify-center items-center">
          <Back v-if="isMobile" @click="back"></Back>
        </div>
        <div class="flex justify-center place-items-center">
          <Save v-if="hasChange" class="mx-8" @click="() => save()"></Save>
        </div>
        <div class="flex justify-center items-center ml-auto">
          <Close v-if="!isMobile" @click="back"></Close>
        </div>
      </div>
      <div class="z-10 flex items-center shrink-0 shadow-md p-4">
        <img class="w-12 h-12 mx-2 object-contain shrink-0" :src="getPlatformUrl(accountRecord.platform)" alt="">
        <div class="flex w-full h-full ml-4s" :title="accountRecord.platform">
          <Description class="w-full" v-model="accountRecord.platform" :horizontal="true">平台</Description>
        </div>
      </div>
      <div ref="elemDescription" class="space-y-4 p-4 h-full overflow-auto bg-gray-50">
        <Description v-model="accountRecord.account">账号</Description>
        <Description v-model="accountRecord.password">密码</Description>
        <Description v-model="accountRecord.note" :multiline="true">备注</Description>
        <div class="flex justify-center px-4 py-2 bg-red-500 text-white rounded-lg cursor-pointer"
          @click="checkDeleteAccount">
          删除
        </div>
      </div>
      <YesNoPrompt :status="yesNoPromptStatus" :yes="'保存'" :no="'不保存'" @confirm="() => save(true)" @cancel="close">
        是否保存修改
      </YesNoPrompt>
      <YesNoPrompt :status="deletePromptStatus" :yes="'删除'" @confirm="deleteAccount" @close="closeDeletePrompt">
        确认删除
      </YesNoPrompt>
    </div>
    <div class="absolute left-0 top-0 w-full h-full bg-neutral-500 bg-opacity-5" @click="back">
    </div>
  </div>
</template>

<style scoped>
@keyframes con-detail {
  100% {
    visibility: hidden;
  }
}

.com-detail:not([data-opened="true"]) {
  animation: 0.3s linear forwards con-detail;
}

.com-detail-slab {
  @apply left-0 bg-red-500;
}
</style>
