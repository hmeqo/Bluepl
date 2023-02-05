import { reactive, ref, watch } from 'vue'
import axios from 'axios'
import worker from './worker'
import CryptoJS from 'crypto-js'
import { sha256hexdigest } from './util'
import { E_net_error, E_out_of_limit, L_not_acount, L_wait_verify } from './status'

export const servers = [
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
]

class AES {

    iv = CryptoJS.enc.Utf8.parse('010203040506070')

    encrypt(text: string): string {
        return CryptoJS.AES.encrypt(CryptoJS.enc.Utf8.parse(text), CryptoJS.enc.Utf8.parse(net.session.key), {
            // iv: this.iv,
            // mode: CryptoJS.mode.CBC,
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7,
        }).toString()
    }

    decrypt(encrypted: string): string {
        return CryptoJS.AES.decrypt(encrypted, CryptoJS.enc.Utf8.parse(net.session.key), {
            // iv: this.iv,
            // mode: CryptoJS.mode.CBC,
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7,
        }).toString(CryptoJS.enc.Utf8)
    }
}

class Net {
    api = reactive({
        async validateSession(): Promise<boolean> {
            return await axios.post(
                '/session/validate',
                { id: net.session.id }
            ).then(response => {
                net.status = 200
                var result = response.data.available
                if (!result) {
                    net.session.clear()
                }
                return result
            }).catch(error => {
                net.status = error.response.status
                return false
            })
        },

        /** 请求并更新 session, 成功返回 true, 否则 false */
        async requestSession() {
            if (net.session.id && await net.api.validateSession()) {
                return true
            }
            var data = await worker?.postMessage('session')
                .then(async (data: any) => {
                    return await axios.post(
                        './session/create',
                        {
                            g: data.g.toString(),
                            p: data.p.toString(),
                            key: data.key.toString(),
                        },
                    ).then(async response => {
                        net.status = 200
                        return { key: BigInt(response.data.key), e: data.e, p: data.p }
                    }).catch(error => {
                        net.status = error.response.status
                        return null
                    })
                })
            if (!data) {
                net.session.clear()
                return false
            }
            var key: string = await worker?.postMessage('session', [data.key, data.e, data.p])
                .then(async (key: bigint) => {
                    return key.toString()
                })
            net.session.key = (await sha256hexdigest(key)).slice(0, 32)
            net.session.id = await sha256hexdigest(net.session.key)
            return true
        },

        /** 返回 status */
        async login(): Promise<number> {
            var data = aes.encrypt(JSON.stringify({
                email: net.user.email,
                password: net.user.password,
            }))
            var digest = await sha256hexdigest(net.session.key + data)
            var status = await axios.post(
                '/login',
                {
                    sessionId: net.session.id,
                    digest: digest,
                    data: data,
                },
            ).then(response => {
                net.status = 200
                return response.data.status
            }).catch(error => {
                net.status = error.response.status
                return E_net_error
            })
            return status
        }
    })
    session = reactive({
        // session id 和 key
        id: localStorage.getItem('sessionId') || '',
        key: localStorage.getItem('sessionKey') || '',

        clear() {
            net.session.id = ''
            net.session.key = ''
        },
    })
    user = reactive({
        // 登录信息
        server: localStorage.getItem('sessionServer') || servers[0].strAddr,
        email: localStorage.getItem('sessionEmail') || '',
        password: localStorage.getItem('sessionPassword') || '',
        veriCode: '',
        // 是否登录成功
        logined: false,
    })
    aes = ref(new AES())
    status = ref(200)

    constructor() {
        // watch(this.status, () => {
        //     console.log(`Status: ${net.status}`)
        // })
        watch(this.session, () => {
            if (this.session.id && this.session.key) {
                console.log(this.session.id)
                console.log(this.session.key)
                localStorage.setItem('sessionId', this.session.id)
                localStorage.setItem('sessionKey', this.session.key)
            }
        })
        watch(this.user, () => {
            if (this.user.logined) {
                localStorage.setItem('sessionServer', this.user.server)
                localStorage.setItem('sessionEmail', this.user.email)
                localStorage.setItem('sessionPassword', this.user.password)
            }
        })
    }
}

export const aes = reactive(new AES())

export const net = reactive(new Net())

export default net
