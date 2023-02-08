<script>
import { webapi } from '../js/globals'
export default {
    data() { return {} },
    methods: {
        async logout() {
            await webapi.logout()
        },
    },
}
</script>

<template>
    <div>
        <button @click="logout">退出登录</button>
    </div>
</template>
