import { reactive } from 'vue'
import axios from 'axios'
import worker from './worker'
import CryptoJS from 'crypto-js'
import { sha256hexdigest } from './util'
import { S_NOT_INTERNET_ERROR } from './status'

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
    iv: CryptoJS.enc.Utf8.parse('010203040506070'),

    encrypt(text: string): string {
        return CryptoJS.AES.encrypt(CryptoJS.enc.Utf8.parse(text), CryptoJS.enc.Utf8.parse(session.key), {
            // iv: this.iv,
            // mode: CryptoJS.mode.CBC,
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7,
        }).toString()
    },

    decrypt(encrypted: string): string {
        return CryptoJS.AES.decrypt(encrypted, CryptoJS.enc.Utf8.parse(session.key), {
            // iv: this.iv,
            // mode: CryptoJS.mode.CBC,
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7,
        }).toString(CryptoJS.enc.Utf8)
    },
})

export const webapi = reactive({
    status: 0,

    async postData(url: string, data?: Object) {
        return await axios.post(url, data)
            .then(response => {
                var data = response.data
                webapi.status = data.status
                return data
            })
            .catch(error => {
                webapi.status = S_NOT_INTERNET_ERROR
                return null
            })
    },

    async postUserData(url: string, data?: Object) {
        var b = aes.encrypt(JSON.stringify(data))
        var digest = await sha256hexdigest(session.key + b)
        return await axios.post(url, {
            sessionId: session.id,
            digest: digest,
            data: b,
        }).then(response => {
            var data = JSON.parse(aes.decrypt(response.data))
            webapi.status = data.status
            return data
        }).catch(error => {
            webapi.status = S_NOT_INTERNET_ERROR
            return null
        })
    },

    async getSessionInfo() {
        return await webapi.postData('/session/info', { id: session.id })
    },

    async requestSession() {
        // 在新线程中计算DH算法所需的 p, g, key
        var data: bigint[] = await worker?.postMessage('session')
            .then(async (data: any) => {
                var responseData = await webapi.postData('/session/create', {
                    g: data.g.toString(),
                    p: data.p.toString(),
                    key: data.key.toString(),
                })
                if (webapi.status == S_NOT_INTERNET_ERROR) {
                    return []
                }
                return [BigInt(responseData.key), data.e, data.p]
            })
        if (!data) {
            return null
        }
        var session_key: string = await worker?.postMessage('session', data)
            .then(async (key: bigint) => {
                return (await sha256hexdigest(key.toString())).slice(0, 32)
            })
        var session_id = await sha256hexdigest(session_key)
        return { key: session_key, id: session_id }
    },

    async login() {
        return await webapi.postUserData('/login', {
            email: user.email,
            password: user.password,
            veriCode: user.veriCode,
        })
    },

    async logout() {
        return await webapi.postUserData('/logout', {})
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

export const user = reactive({
    // 登录信息
    server: localStorage.getItem('sessionServer') || servers[0].strAddr,
    email: localStorage.getItem('sessionEmail') || '',
    password: localStorage.getItem('sessionPassword') || '',
    veriCode: '',

    name: '',

    loggingIn: false,
    // 是否登录成功
    logined: false,

    data: {
        accounts: [
            {
                id: 1,
                platform: '',
                account: '',
                password: '',
                note: '',
            },
            {
                id: 1,
                platform: '',
                account: '',
                password: '',
                note: '',
            },
            {
                id: 1,
                platform: '',
                account: '',
                password: '',
                note: '',
            },
        ],

        platformToImgUrl: {
            '': '/logos/unknow.png',
            'qq': '/logos/qq.png',
            'wechat': '/logos/wechat.png',
            '微信': '/logos/wechat.png',
        },
    },

    save_account() {
        localStorage.setItem('sessionServer', user.server)
        localStorage.setItem('sessionEmail', user.email)
        localStorage.setItem('sessionPassword', user.password)
    },

    clear_account() {
        user.password = ''
        user.veriCode = ''
        user.data.accounts = []
        user.save_account()
    },
})

export default {
    servers,
    session,
    webapi,
    aes,
    user,
}
