import { reactive, UnwrapNestedRefs } from 'vue'
import axios from 'axios'
import worker from './worker'
import CryptoJS from 'crypto-js'
import { sha256hexdigest } from './util'
import { S_NOT_INTERNET_ERROR, S_SESSION_ERROR, S_SUCCESS_200 } from './status'
import { app } from './app'
import { AccountType } from './types'

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

    /** 请求明文数据 */
    async postData(url: string, data?: Object) {
        for (const i in webapi.onRequestStart)
            webapi.onRequestStart[i]()
        var response = await axios.post(url, data)
            .then(response => {
                return response.data
            })
            .catch(() => { return { status: S_NOT_INTERNET_ERROR } })
        for (const i in webapi.onRequestEnd)
            webapi.onRequestEnd[i](response.status)
        return response
    },

    /** 请求加密数据 */
    async postEncryptedData(url: string, data?: Object) {
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
                if (response.data instanceof Object) {
                    return response.data
                } else {
                    return JSON.parse(aes.decrypt(response.data))
                }
            }).catch(() => {
                return { status: S_NOT_INTERNET_ERROR }
            })
            if (response.status == S_SESSION_ERROR) {
                if (!await app.createSession()) { break }
            }
        } while (response.status == S_SESSION_ERROR);
        for (const i in webapi.onRequestEnd)
            webapi.onRequestEnd[i](response.status)
        return response
    },

    /** 获取session状态 */
    async getSessionStatus() {
        return await webapi.postData('/session/status', { id: session.id })
    },

    async createSession() {
        // 在新线程中计算DH算法所需的 p, g, key
        var data: bigint[] = await worker?.postMessage('dh')
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
        session.key = await worker?.postMessage('dh', data)
            .then(async (key: bigint) => {
                return (await sha256hexdigest(key.toString())).slice(0, 32)
            })
        session.id = await sha256hexdigest(session.key)
        session.save()
        return { status: S_SUCCESS_200 }
    },

    async login(email: string, password: string, veriCode?: string) {
        return await webapi.postEncryptedData('/login', {
            email: email,
            password: password,
            veriCode: veriCode,
        })
    },

    async logout() {
        return await webapi.postEncryptedData('/logout', {})
    },

    async hadUser(uid?: number, email?: string) {
        return await webapi.postEncryptedData('/user/had', { uid, email })
    },

    async resetPassword(email: string, password?: string, veriCode?: string) {
        return await webapi.postEncryptedData('/user/resetpassword', { email, password, veriCode })
    },

    async getUserInfo() {
        return await webapi.postEncryptedData('/user/info', {})
    },

    async updateUserInfo(name?: string) {
        return await webapi.postEncryptedData('/user/updateinfo', { name })
    },

    async getDataAccounts() {
        return await webapi.postEncryptedData('/user/accounts', {})
    },

    async createDataAccount(account?: AccountType) {
        return await webapi.postEncryptedData('/user/accounts/create', account || {})
    },

    async updateDataAccount(account: AccountType) {
        return await webapi.postEncryptedData('/user/accounts/update', account)
    },

    async deleteDataAccount(account_id: number) {
        return await webapi.postEncryptedData('/user/accounts/delete', { "id": account_id })
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

export default {
    session,
    webapi,
    aes,
}
