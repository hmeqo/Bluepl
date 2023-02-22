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
    var url = user.data.platformToImgUrl[platform?.toLowerCase().trim() || '']
    return url || user.data.platformToImgUrl['']
}

export const app = reactive({
    inited: false,

    currentAccountId: -1,

    async init() {
        await app.requestSession()
        app.inited = true
    },

    async requestSession() {
        var response = await webapi.getSessionInfo()
        if (response.status == S_SUCCESS_200) {
            if (response.logined) {
                user.logined = true
            }
            return true
        }
        if (response.status == S_NOT_INTERNET_ERROR) {
            return false
        }
        return (await webapi.requestSession()).status == S_SUCCESS_200
    },

    async login(email: string, password: string, veriCode?: string) {
        user.loggingIn = true
        var status: number = (await webapi.login(email, password, veriCode)).status
        if (status == S_SUCCESS_200) {
            user.save_account()
            user.logined = true
        } else {
            user.logined = false
        }
        user.loggingIn = false
        return status
    },

    async logout() {
        await webapi.logout()
        user.clear_account()
        user.logined = false
    },

    async hadUser(uid?: number, email?: string) {
        var response = await webapi.hadUser(uid, email)
        if (response.status != S_SUCCESS_200) {
            return false
        }
        return response.hadUser == true
    },

    async getUserInfo() {
        var response = await webapi.getUserInfo()
        if (response.status != S_SUCCESS_200) {
            return false
        }
        var info = response.data
        user.uid = info.uid
        user.name = info.name
        user.avatar = info.avatar
        return true
    },

    async getDataAccount() {
        var response = await webapi.getDataAccounts()
        if (response.status != S_SUCCESS_200) {
            return false
        }
        var data = response.data
        for (const i in data) {
            user.data.accounts.push(data[i])
        }
        return true
    },

    async createDataAccount() {
        var response = await webapi.createDataAccount()
        if (response.status != S_SUCCESS_200) {
            return null
        }
        var account = {
            id: response.id,
            platform: '',
            account: '',
            password: '',
            note: '',
        }
        user.data.accounts.push(account)
        app.currentAccountId = response.id
        return account
    },

    async updateDataAccount(accounts: Array<accountType>) {
        var response = await webapi.updateDataAccounts(accounts)
        if (response.status != S_SUCCESS_200) {
            // TODO 数据更新失败
            return false
        }
        return true
    },

    async deleteDataAccount(account_ids: Array<number>) {
        var response = await webapi.deleteDataAccounts(account_ids)
        if (response.status != S_SUCCESS_200) {
            // TODO 数据更新失败
            return false
        }
        user.data.accounts = user.data.accounts.filter((account: accountType) => {
            for (const i in account_ids) {
                if (account.id == account_ids[i]) {
                    return false
                }
            }
            return true
        })
        return true
    },
})
