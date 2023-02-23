import { reactive, UnwrapNestedRefs } from 'vue'
import axios from 'axios'
import worker from './worker'
import CryptoJS from 'crypto-js'
import { sha256hexdigest } from './util'
import { S_NOT_INTERNET_ERROR, S_SESSION_ERROR, S_SUCCESS_200 } from './status'
import { app } from './app'

export type accountType = {
    id: number,
    platform: string,
    account: string,
    password: string,
    note: string,
}

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

export const aes = reactive({
    iv: CryptoJS.enc.Utf8.parse('0102030405060708'),

    encrypt(text: string): string {
        return CryptoJS.AES.encrypt(CryptoJS.enc.Utf8.parse(text), CryptoJS.enc.Utf8.parse(session.key), {
            iv: this.iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7,
        }).toString()
    },

    decrypt(encrypted: string): string {
        return CryptoJS.AES.decrypt(encrypted, CryptoJS.enc.Utf8.parse(session.key), {
            iv: this.iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7,
        }).toString(CryptoJS.enc.Utf8)
    },
})

export const webapiOnRequestStart: UnwrapNestedRefs<Array<Function>> = reactive([])

export const webapiOnRequest: UnwrapNestedRefs<Array<Function>> = reactive([])

export const webapi = reactive({
    onRequestStart: webapiOnRequestStart,
    onRequestEnd: webapiOnRequest,

    async postData(url: string, data?: Object) {
        for (const i in webapi.onRequestStart)
            webapi.onRequestStart[i]()
        var response = await axios.post(url, data)
            .then(response => { return response.data })
            .catch(() => { return { status: S_NOT_INTERNET_ERROR } })
        for (const i in webapi.onRequestEnd)
            webapi.onRequestEnd[i](response.status)
        return response
    },

    async postUserData(url: string, data?: Object) {
        for (const i in webapi.onRequestStart)
            webapi.onRequestStart[i]()
        do {
            var encryptedData = aes.encrypt(JSON.stringify(data))
            var digest = await sha256hexdigest(session.key + encryptedData)
            var response = await axios.post(url, {
                sessionId: session.id,
                digest: digest,
                data: encryptedData,
            }).then(response => {
                try {
                    return JSON.parse(aes.decrypt(response.data))
                } catch (error) {
                    return { status: S_SESSION_ERROR }
                }
            }).catch(() => {
                return { status: S_NOT_INTERNET_ERROR }
            })
            if (response.status == S_SESSION_ERROR) {
                if (!await app.requestSession()) { break }
            }
        } while (response.status == S_SESSION_ERROR);
        for (const i in webapi.onRequestEnd)
            webapi.onRequestEnd[i](response.status)
        return response
    },

    async getSessionInfo() {
        return await webapi.postData('/session/info', { id: session.id })
    },

    async createSession() {
        // 在新线程中计算DH算法所需的 p, g, key
        var data: bigint[] = await worker?.postMessage('session')
            .then(async (data: any) => {
                var responseData = await webapi.postData('/session/create', {
                    g: data.g.toString(),
                    p: data.p.toString(),
                    key: data.key.toString(),
                })
                if (responseData.status == S_NOT_INTERNET_ERROR) {
                    return []
                }
                return [BigInt(responseData.key), data.e, data.p]
            })
        if (!data.length) {
            return { status: S_NOT_INTERNET_ERROR }
        }
        session.key = await worker?.postMessage('session', data)
            .then(async (key: bigint) => {
                return (await sha256hexdigest(key.toString())).slice(0, 32)
            })
        session.id = await sha256hexdigest(session.key)
        session.save()
        return { status: S_SUCCESS_200 }
    },

    async login(email: string, password: string, veriCode?: string) {
        return await webapi.postUserData('/login', {
            email: email,
            password: password,
            veriCode: veriCode,
        })
    },

    async logout() {
        return await webapi.postUserData('/logout', {})
    },

    async hadUser(uid?: number, email?: string) {
        return await webapi.postData('/user/had', { uid, email })
    },

    async resetPassword(email: string, password?: string, veriCode?: string) {
        return await webapi.postData('/user/resetpassword', { email, password, veriCode })
    },

    async updateUserInfo(name?: string) {
        return await webapi.postUserData('/user/updateinfo', { name })
    },

    async getUserInfo() {
        return await webapi.postUserData('/user/info', {})
    },

    async getDataAccounts() {
        return await webapi.postUserData('/user/accounts', {})
    },

    async createDataAccount() {
        return await webapi.postUserData('/user/accounts/create', {})
    },

    async updateDataAccounts(accounts: Array<accountType>) {
        return await webapi.postUserData('/user/accounts/update', accounts)
    },

    async deleteDataAccounts(account_ids: Array<number>) {
        return await webapi.postUserData('/user/accounts/delete', account_ids)
    },
})

export const session = reactive({
    // session id 和 key
    id: localStorage.getItem('sessionId') || '',
    key: localStorage.getItem('sessionKey') || '',

    save() {
        localStorage.setItem('sessionId', session.id)
        localStorage.setItem('sessionKey', session.key)
    },

    clear() {
        session.id = ''
        session.key = ''
        session.save()
    },
})

export const userAccounts: UnwrapNestedRefs<Array<accountType>> = reactive([])

export const user = reactive({
    // 登录信息
    server: localStorage.getItem('sessionServer') || servers[0].strAddr,
    email: localStorage.getItem('sessionEmail') || '',
    password: '',

    uid: 0,
    name: '',
    avatar: '',

    loggingIn: false,
    // 是否登录成功
    logined: false,

    data: {
        accounts: userAccounts,
        platformToImgUrl: {
            '': '/logos/unknow.webp',
            'qq': '/logos/qq.webp',
            'wechat': '/logos/wechat.webp',
            '微信': '/logos/wechat.webp',
        },
    },

    save_account() {
        localStorage.setItem('sessionServer', user.server)
        localStorage.setItem('sessionEmail', user.email)
    },

    clear_account() {
        user.data.accounts = []
        localStorage.clear()
    },
})

export default {
    servers,
    session,
    webapi,
    aes,
    user,
}
