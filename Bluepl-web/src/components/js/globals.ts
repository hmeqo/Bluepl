import { reactive, ref, watch } from 'vue'
import axios from 'axios'
import worker from './worker'
import CryptoJS from 'crypto-js'
import { sha256hexdigest } from './util'
import { S_NOT_INTERNET_ERROR, S_SUCCESS_200 } from './status'
import { app } from './app'

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

    async getSessionInfo() {
        return await axios.post(
            '/session/info',
            { id: session.id }
        ).then(response => {
            webapi.status = S_SUCCESS_200
            var result = response.data
            if (!result) {
                session.clear()
            }
            return { "logined": result.logined, "available": result.available }
        }).catch(error => {
            console.log(error)
            webapi.status = S_NOT_INTERNET_ERROR
            return { "logined": false, "available": false }
        })
    },

    /** 请求并更新 session 返回状态码 */
    async requestSession() {
        var session_info = await webapi.getSessionInfo()
        if (session.id && session_info.available || webapi.status == S_NOT_INTERNET_ERROR) {
            if (session_info.logined && user.email) {
                user.logined = true
            }
            return webapi.status
        }
        // 在新线程中计算DH算法所需的 p, g, key
        var data: bigint[] = await worker?.postMessage('session')
            .then(async (data: any) => {
                // 等待服务器完成剩下的计算部分
                return await axios.post(
                    './session/create',
                    {
                        g: data.g.toString(),
                        p: data.p.toString(),
                        key: data.key.toString(),
                    },
                ).then(response => {
                    webapi.status = S_SUCCESS_200
                    return [BigInt(response.data.key), data.e, data.p]
                }).catch(error => {
                    console.log(error)
                    webapi.status = S_NOT_INTERNET_ERROR
                    return []
                })
            })
        if (!data) {
            session.clear()
            return webapi.status
        }
        var session_key: string = await worker?.postMessage('session', data)
            .then(async (key: bigint) => {
                return (await sha256hexdigest(key.toString())).slice(0, 32)
            })
        var session_id = await sha256hexdigest(session_key)
        session.key = session_key
        session.id = session_id
        session.save()
        return webapi.status
    },

    async creatSessionData(json_data: any) {
        var data = aes.encrypt(JSON.stringify(json_data))
        var digest = await sha256hexdigest(session.key + data)
        return {
            sessionId: session.id,
            digest: digest,
            data: data,
        }
    },

    /** 返回 status */
    async login(): Promise<number> {
        user.loggingIn = true
        await axios.post(
            '/login',
            await webapi.creatSessionData({
                email: user.email,
                password: user.password,
                veriCode: user.veriCode,
            }),
        ).then(response => {
            var data = JSON.parse(aes.decrypt(response.data))
            webapi.status = data.status
        }).catch(error => {
            console.log(error)
            webapi.status = S_NOT_INTERNET_ERROR
        })
        if (webapi.status == S_SUCCESS_200) {
            user.save()
            user.logined = true
            app.currentScreen = 1
            await webapi.requestUserDataAccounts()
        } else {
            user.clear()
            user.logined = false
        }
        user.loggingIn = false
        return webapi.status
    },

    async logout() {
        await axios.post(
            '/logout',
            await webapi.creatSessionData({}),
        ).then(response => {
            var data = JSON.parse(aes.decrypt(response.data))
            webapi.status = data.status
        }).catch(error => {
            console.log(error)
            webapi.status = S_NOT_INTERNET_ERROR
        })
        user.clear()
        user.data.accounts = []
        user.logined = false
        return webapi.status
    },

    async requestUserDataAccounts() {
        var data: object = await axios.post(
            '/user/accounts',
            await webapi.creatSessionData({}),
        ).then(response => {
            var data = JSON.parse(aes.decrypt(response.data))
            webapi.status = data.status
            return data.data
        }).catch(error => {
            console.log(error)
            webapi.status = S_NOT_INTERNET_ERROR
            return {}
        })
        if (webapi.status == S_SUCCESS_200) {
            for (const i in data) {
                user.data.accounts.push(data[i])
            }
        }
        return webapi.status
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

    loggingIn: false,
    // 是否登录成功
    logined: false,

    data: {
        accounts: [
            {
                id: 1,
                platform: 'QQ',
                account: '1875557990',
                password: '123123',
                note: '我的QQ账号',
            },
            {
                id: 2,
                platform: 'QQ',
                account: '1875557990',
                password: '123123',
                note: '我的QQ账号',
            },
        ],

        platformToImgUrl: {
            '': '/logos/not.png',
            'QQ': '/logos/qq.png',
        },

        save(account?: any) {
            // webapi.
        },

        request() {

        },
    },

    save() {
        localStorage.setItem('sessionServer', user.server)
        localStorage.setItem('sessionEmail', user.email)
        localStorage.setItem('sessionPassword', user.password)
    },

    clear() {
        user.password = ''
        user.veriCode = ''
        user.save()
    },
})

export default {
    servers,
    session,
    webapi,
    aes,
    user,
}

user.data.accounts = []
