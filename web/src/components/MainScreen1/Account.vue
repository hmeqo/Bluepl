<script lang="ts" setup>
import { app, user } from '../js/app';
import { AccountType } from '../js/types';

const props = defineProps<{
  account: AccountType,
}>()

function showDetail() {
  app.currentAccountId = props.account.id
}
</script>

<template>
  <div
    class="group main flex p-3 transition-colors cursor-pointer rounded-xl shadow-sm overflow-hidden bg-white hover:bg-blue-500"
    @click="showDetail">
    <div class="shrink-0 pr-3">
      <img class="w-12 h-12 mx-4 object-contain" :src="user.dataAccount.getPlatformUrl(account.platform)" alt="">
      <div class="mt-1 text-sm text-center transition-colors group-hover:text-white">
        {{ account.platform }}
      </div>
    </div>
    <div class="space-y-1 w-full h-full">
      <div class="text-lg transition-colors group-hover:text-white">
        {{ account.account }}
      </div>
      <div class="text-sm text-neutral-600 transition-colors group-hover:text-neutral-200" :title="account.note">
        {{ account.note }}
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
