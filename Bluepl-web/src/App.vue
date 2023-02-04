<script lang="ts" setup>
import { app } from './components/js/globals'
import Login from './components/Login.vue'
import Loading from './components/Loading.vue'

app.init()
</script>

<template>
  <div class="w-screen h-screen grid bg-primary-900 box-border overflow-auto">
    <Loading v-if="!app.inited" :pattern="1"></Loading>
    <Login></Login>
  </div>
</template>
