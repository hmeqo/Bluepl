import { reactive, ref } from 'vue'
import { net } from './network'

class App {
    status = ref(0)

    inited = ref(false)

    public async init() {
        await net.api.requestSession()
        app.inited = true
    }
}

export const app = reactive(new App())

export const globals = reactive({
    app,
})

export default globals
