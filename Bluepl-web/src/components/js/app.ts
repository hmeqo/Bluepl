import { reactive } from "vue";
import { accountType, session, user, webapi } from "./globals";
import { S_NOT_INTERNET_ERROR, S_SUCCESS_200 } from "./status";

export function getAccountById(accountId: number) {
    for (const i in user.data.accounts) {
        var a = user.data.accounts[i]
        if (a.id == accountId) {
            return user.data.accounts[i]
        }
    }
    return user.data.accounts[0]
}

export function getPlatformUrl(platform: string | null) {
    return user.data.platformToImgUrl[platform?.toLowerCase() || '']
}

export const app = reactive({
    inited: false,

    currentScreen: 1,

    currentAccountId: -1,

    async init() {
        await app.requestSession()
        if (webapi.status == S_SUCCESS_200 && user.email && user.password) {
            await webapi.login()
        }
        app.inited = true
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
        if (webapi.status == S_SUCCESS_200) {
            app.currentScreen = 1
            user.logined = true
            user.save_account()
            await app.getDataAccount()
        } else {
            user.logined = false
        }
        user.loggingIn = false
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
        if (webapi.status != S_SUCCESS_200) {
            return
        }
        var account = {
            id: data.id,
            platform: '',
            account: '',
            password: '',
            note: '',
        }
        user.data.accounts.push(account)
        app.currentAccountId = data.id
        return account
    },

    async updateDataAccount(accounts: Array<accountType>) {
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
        user.data.accounts = user.data.accounts.filter((account: accountType) => {
            for (const i in account_ids) {
                if (account.id == account_ids[i]) {
                    return false
                }
            }
            return true
        })
    },
})
