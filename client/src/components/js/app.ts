import { reactive, Ref, ref, UnwrapNestedRefs } from "vue"
import { webapi } from "./webapi"
import { AccountType } from './types'
import { S_NOT_INTERNET_ERROR, S_SESSION_ERROR, S_SUCCESS_200 } from "./status"

export const TEMP_ID = 0

export const servers = reactive([
    {
        name: '本地',
        ip: '127.0.0.1',
        port: 8000,
        strAddr: '127.0.0.1:8000',
    },
    {
        name: 'AAA',
        ip: '127.0.0.1',
        port: 8001,
        strAddr: '127.0.0.1:8001',
    },
])

export const userDataAccounts: UnwrapNestedRefs<Array<AccountType>> = reactive([])

export const user = reactive({
    server: localStorage.getItem('sessionServer') || servers[0].strAddr,
    email: localStorage.getItem('sessionEmail') || '',
    password: '',

    uid: 0,
    name: '',
    avatar: '',

    dataAccount: {
        list: userDataAccounts,

        platformToImgUrl: {
            '': '/logos/unknow.webp',
            'qq': '/logos/qq.webp',
            'wechat': '/logos/wechat.webp',
            '微信': '/logos/wechat.webp',
            'steam': '/logos/steam.webp',
        },

        /** 清空 */
        clear() {
            user.dataAccount.list = []
        },

        /** 通过id获取账号数据 */
        getById(accountId: number | null) {
            if (accountId == null) {
                return user.dataAccount.list[0]
            }
            for (const i in user.dataAccount.list) {
                var account = user.dataAccount.list[i]
                if (account.id == accountId) {
                    return user.dataAccount.list[i]
                }
            }
            return user.dataAccount.list[0]
        },

        /** 获取平台图像url */
        getPlatformUrl(platform: string | null) {
            var url = user.dataAccount.platformToImgUrl[platform?.toLowerCase().trim() || '']
            return url || user.dataAccount.platformToImgUrl['']
        }
    },

    /** 记住当前用户 */
    record() {
        localStorage.setItem('sessionServer', user.server)
        localStorage.setItem('sessionEmail', user.email)
    },

    getAvatar() {
        return user.avatar || '/useravatar/default.png'
    }
})

export const appCurrentAccountId: Ref<number | null> = ref(null)

export const app = reactive({
    inited: false,

    loading: false,

    loggingIn: false,

    logined: false,

    /** 当前要显示详细信息的账号数据id */
    currentAccountId: appCurrentAccountId,

    async init() {
        app.loading = true
        await app.createSession()
        app.loading = false
        app.inited = true
    },

    /** 初始化用户数据 */
    async initializeUserData() {
        app.logined = true
        user.dataAccount.clear()
        user.record()
        await app.getUserInfo()
        await app.getDataAccount()
    },

    /** 创建 Session 会话并尝试登录, 返回状态码 */
    async createSession(): Promise<number> {
        var response = await webapi.getSessionStatus()
        if (response.status == S_NOT_INTERNET_ERROR) {
            return S_NOT_INTERNET_ERROR
        }
        if (response.logined) {
            await app.initializeUserData()
            return S_SUCCESS_200
        }
        if (response.status == S_SESSION_ERROR) {
            response = await webapi.createSession()
        }
        if (response.status == S_SUCCESS_200 && user.password) {
            return await app.login(user.email, user.password)
        }
        app.logined = false
        return response.status
    },

    /** 登录, 返回状态码 */
    async login(email: string, password: string, veriCode?: string): Promise<number> {
        app.loggingIn = true
        var status: number = (await webapi.login(email, password, veriCode)).status
        if (status == S_SUCCESS_200) {
            user.email = email
            user.password = password
            await app.initializeUserData()
        } else {
            app.logined = false
        }
        app.loggingIn = false
        return status
    },

    /** 退出登录 */
    async logout() {
        await webapi.logout()
        user.password = ''
        user.dataAccount.clear()
        app.logined = false
    },

    /** 该用户是否存在 */
    async hadUser(uid?: number, email?: string): Promise<boolean | null> {
        var response = await webapi.hadUser(uid, email)
        if (response.status == S_NOT_INTERNET_ERROR) {
            return null
        }
        if (response.status != S_SUCCESS_200) {
            return false
        }
        return response.hadUser == true
    },

    /** 重置密码 */
    async resetPassword(email: string, password?: string, veriCode?: string): Promise<number> {
        // TODO
        return (await webapi.resetPassword(email, password, veriCode)).status
    },

    /** 更新用户信息 */
    async updateUserInfo(name: string): Promise<boolean> {
        return (await webapi.updateUserInfo(name)).status == S_SUCCESS_200
    },

    /** 获取用户信息 */
    async getUserInfo(): Promise<boolean> {
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

    /** 获取存储的账号数据 */
    async getDataAccount(): Promise<boolean> {
        var response = await webapi.getDataAccounts()
        if (response.status != S_SUCCESS_200) {
            return false
        }
        var data = response.data
        for (const i in data) {
            user.dataAccount.list.push(data[i])
        }
        return true
    },

    /** 创建一个账号数据 */
    async createDataAccount(): Promise<AccountType> {
        var account = {
            id: TEMP_ID,
            platform: '',
            account: '',
            password: '',
            note: '',
        }
        user.dataAccount.list.push(account)
        app.currentAccountId = TEMP_ID
        return account
    },

    /** 更新账号数据 */
    async updateDataAccount(account: AccountType): Promise<boolean> {
        if (account.id == TEMP_ID) {
            var response = await webapi.createDataAccount(account)
            if (response.status != S_SUCCESS_200) {
                return false
            }
            account.id = response.id
            return true
        }
        var response = await webapi.updateDataAccount(account)
        if (response.status != S_SUCCESS_200) {
            // TODO 数据更新失败
            return false
        }
        return true
    },

    /** 删除账号数据 */
    async deleteDataAccount(account_id: number): Promise<boolean> {
        if (account_id != TEMP_ID) {
            var response = await webapi.deleteDataAccount(account_id)
            if (response.status != S_SUCCESS_200) {
                // TODO 数据更新失败
                return false
            }
        }
        user.dataAccount.list = user.dataAccount.list.filter((account: AccountType) => {
            if (account.id == account_id) {
                return false
            }
            return true
        })
        return true
    },
})
