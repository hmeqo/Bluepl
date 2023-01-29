// @ts-check
import { ref, reactive } from 'vue'

const servers = [
    {
        name: '本地',
        ip: '127.0.0.1',
        port: 8000,
        strAddr: '127.0.0.1:8000',
    },
]

const attrs = reactive({
    server: ref(servers[0]),
    servers: servers,
})

export default attrs
