import { reactive } from "vue";
import { user, webapi } from "./globals";
import { S_SUCCESS_200 } from "./status";

export const app = reactive({
    currentScreen: 1,
    inited: false,

    async init() {
        await webapi.requestSession()
        if (webapi.status == S_SUCCESS_200 && user.email && user.password) {
            await webapi.login()
        }
        app.inited = true
    }
})
