<script lang="ts" setup>
import { ref, watch, reactive, Ref, UnwrapNestedRefs } from 'vue';
import MultilineEntry from './MultilineEntry.vue'
import Back from '../icons/Back.vue'
import Save from '../icons/Save.vue'
import Close from '../icons/Close.vue'
import YesNoPrompt from '../prompts/YesNo.vue'
import { app, user } from '../js/app'
import { AccountType } from '../js/types'
import { isMobile } from '../js/util'

const refRoot = ref(null)

const refEntryContainer = ref(null)

const hasChange = ref(false)

const yesNoPromptStatus = reactive({ opened: false })

const deletePromptStatus = reactive({ opened: false })

const hintPromptStatus = reactive({ opened: false, hintText: '' })

const currentAccount: Ref<AccountType> = ref({
  id: -1,
  platform: '',
  account: '',
  password: '',
  note: '',
})

const accountRecord: UnwrapNestedRefs<AccountType> = reactive({
  id: -1,
  platform: '',
  account: '',
  password: '',
  note: '',
})

watch(app, () => {
  if (app.currentAccountId != null) {
    currentAccount.value = user.dataAccount.getById(app.currentAccountId)
    accountRecord.id = currentAccount.value.id
    accountRecord.platform = currentAccount.value.platform
    accountRecord.account = currentAccount.value.account
    accountRecord.password = currentAccount.value.password
    accountRecord.note = currentAccount.value.note
    setTimeout(() => {
      var elem: any = refRoot.value
      elem.focus()
      elem = refEntryContainer.value
      elem.scrollTo(0, 0)
    }, 10)
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
  var success = await app.updateDataAccount(accountRecord)
  if (!success) {
    hintPromptStatus.opened = true
    hintPromptStatus.hintText = "????????????"
    return
  }
  hasChange.value = false
  currentAccount.value = user.dataAccount.getById(app.currentAccountId)
  currentAccount.value.id = accountRecord.id
  currentAccount.value.platform = accountRecord.platform
  currentAccount.value.account = accountRecord.account
  currentAccount.value.password = accountRecord.password
  currentAccount.value.note = accountRecord.note
  if (close_flag) {
    close()
  }
}

function close() {
  app.currentAccountId = null
}

async function deleteAccount() {
  await app.deleteDataAccount(currentAccount.value.id)
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

function keyDown(event: KeyboardEvent) {
  if (event.key == 'Escape') {
    back()
  }
  if (event.ctrlKey && event.key == 's') {
    event.preventDefault()
    save(true)
  }
}
</script>

<template>
  <div class="delay-hidden z-10 absolute top-0 flex justify-center items-center w-full h-full transition-all"
    :class="app.currentAccountId != null ? 'left-0 slab:opacity-100' : 'left-full slab:opacity-0 slab:left-0'"
    :data-hidden="app.currentAccountId == null" ref="refRoot" tabindex="0" @keydown="keyDown">
    <div
      class="z-10 flex flex-col w-full h-full max-h-full py-4 from-gray-50 to-blue-50 bg-gradient-to-br slab:max-w-lg slab:h-auto slab:rounded-lg slab:shadow-md">
      <div class="shrink-0 flex items-center w-full px-4 mb-4">
        <div class="flex items-center">
          <Back class="block slab:hidden" @click="back"></Back>
        </div>
        <div class="flex items-center ml-auto">
          <Save v-if="hasChange" class="mx-8" @click="() => save()"></Save>
          <Close class="hidden slab:block" @click="back"></Close>
        </div>
      </div>
      <div class="flex flex-col overflow-auto">
        <div class="shrink-0 flex items-center p-4">
          <img class="shrink-0 w-12 h-12 mx-2 object-contain" :src="user.dataAccount.getPlatformUrl(accountRecord.platform)" alt="">
          <div class="flex w-full h-full ml-4s" :title="accountRecord.platform">
            <MultilineEntry v-model="accountRecord.platform" :max-length="50" :horizontal="true">??????</MultilineEntry>
          </div>
        </div>
        <div class="grid p-4" ref="refEntryContainer">
          <MultilineEntry v-model="accountRecord.account" :max-length="50" :horizontal="!isMobile">??????</MultilineEntry>
          <MultilineEntry class="mt-6" v-model="accountRecord.password" :max-length="100" :horizontal="!isMobile">??????</MultilineEntry>
          <MultilineEntry class="mt-6" v-model="accountRecord.note" :max-length="200" :horizontal="!isMobile">??????</MultilineEntry>
          <button class="flex justify-center mt-10 px-4 py-2 w-full bg-red-600 text-white rounded-md transition-colors hover:bg-red-700 focus:outline-1"
            @click="checkDeleteAccount">
            ??????
          </button>
        </div>
      </div>
    </div>
    <div class="absolute left-0 top-0 w-full h-full bg-neutral-500 bg-opacity-5" @click="back">
    </div>
    <YesNoPrompt :status="yesNoPromptStatus" :yes="'??????'" :no="'?????????'" @confirm="() => save(true)" @cancel="close">
      ??????????????????
    </YesNoPrompt>
    <YesNoPrompt :status="deletePromptStatus" :yes="'??????'" @confirm="deleteAccount" @close="closeDeletePrompt">
      ????????????
    </YesNoPrompt>
    <YesNoPrompt :status="hintPromptStatus" :yes="'??????'">
      {{ hintPromptStatus.hintText }}
    </YesNoPrompt>
  </div>
</template>
