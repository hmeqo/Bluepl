import { reactive } from "vue";
import { session, user, webapi } from "./globals";
import { S_NOT_INTERNET_ERROR, S_PASSWORD_ERROR, S_SUCCESS_200 } from "./status";

export const app = reactive({
    inited: false,

    currentScreen: 1,

    newAccountId: -1,

    async init() {
        await app.requestSession()
        if (webapi.status == S_SUCCESS_200 && user.email && user.password) {
            await webapi.login()
        }
        app.inited = true
    },

    isNewAccount(account: any) {
        if (app.newAccountId == -1) {
            return false
        }
        if (app.newAccountId == account.id) {
            app.newAccountId = -1
            return true
        }
        return false
    },

    async requestSession() {
        await webapi.getSessionInfo()
        if (webapi.status == S_SUCCESS_200) {
            if (user.email && user.password) {
                await app.login()
            }
            return
        }
        if (webapi.status == S_NOT_INTERNET_ERROR) {
            return
        }
        session.clear()
        var session_info = await webapi.requestSession()
        if (session_info) {
            session.key = session_info.key
            session.id = session_info.id
            session.save()
        }
    },

    async login() {
        user.loggingIn = true
        await webapi.login()
        user.loggingIn = false
        if (webapi.status != S_SUCCESS_200) {
            user.logined = false
            return
        }
        user.save_account()
        await app.getDataAccount()
        if (webapi.status != S_SUCCESS_200) {
            return
        }
        user.logined = true
        app.currentScreen = 1
    },

    async logout() {
        await webapi.logout()
        user.clear_account()
        user.logined = false
    },

    async getDataAccount() {
        var data = (await webapi.getDataAccounts()).data
        user.data.accounts = []
        if (webapi.status != S_SUCCESS_200) {
            return
        }
        for (const i in data) {
            user.data.accounts.push(data[i])
        }
    },

    async createDataAccount() {
        var data = await webapi.createDataAccount()
        console.log(webapi.status)
        if (webapi.status != S_SUCCESS_200) {
            return
        }
        app.newAccountId = data.id
        var account = {
            id: app.newAccountId,
            platform: '',
            account: '',
            password: '',
            note: '',
        }
        user.data.accounts.push(account)
        console.log(user.data.accounts)
        return account
    },

    async updateDataAccount(accounts: Array<{
        id: number,
        platform?: string,
        account?: string,
        password?: string,
        note?: string,
    }>) {
        await webapi.updateDataAccounts(accounts)
        if (webapi.status != S_SUCCESS_200) {
            // TODO 数据更新失败
            return
        }
    },

    async deleteDataAccount(account_ids: Array<number>) {
        await webapi.deleteDataAccounts(account_ids)
        if (webapi.status != S_SUCCESS_200) {
            // TODO 数据更新失败
            return
        }
        user.data.accounts = user.data.accounts.filter((account) => {
            for (const i in account_ids) {
                if (account.id == account_ids[i]) {
                    return false
                }
            }
            return true
        })
    },
})
