<script setup>
import { app } from '../js/app';

async function logout() {
    await app.logout()
}
</script>

<template>
    <div class="flex flex-col w-full h-full">
        <div class="flex justify-center shadow-md rounded-lg mt-auto m-2 px-4 py-2 cursor-pointer" @click="logout">
            退出登录
        </div>
    </div>
</template>
