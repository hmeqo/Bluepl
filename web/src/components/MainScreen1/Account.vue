<script lang="ts" setup>
import { app, getAccountById, getPlatformUrl } from '../js/app';

const props = defineProps<{
  accountId: number,
}>()

const account = getAccountById(props.accountId)

function showDetail() {
  app.currentAccountId = account.id
}
</script>

<template>
  <div class="rounded-2xl shadow-md overflow-hidden bg-white">
    <div class="group main flex p-3 transition-colors cursor-pointer hover:bg-blue-500 bg-opacity-50"
      @click="showDetail">
      <div class="shrink-0">
        <img class="w-12 h-12 mx-4 object-contain" :src="getPlatformUrl(account.platform)" alt="">
        <div class="mt-1 text-sm text-center transition-colors group-hover:text-white" :title="account.platform">
          {{ account.platform }}
        </div>
      </div>
      <div class="space-y-1 w-full h-full ml-3">
        <div class="text-lg transition-colors group-hover:text-white" :title="account.account">{{ account.account }}
        </div>
        <div class="text-neutral-600 transition-colors group-hover:text-neutral-200" :title="account.note">
          {{ account.note }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.main * {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
