import CryptoJS from "crypto-js"

// export const encoder = new TextEncoder()

// export const decoder = new TextDecoder('UTF-8')

// export function encodeUtf8(text: string) {
//     return arrayToString(Array.from(encoder.encode(text)))
// }

// export function stringToArray(s: string) {
//     var array: Array<number> = []
//     for (var i = 0; i < s.length; i++) {
//         array.push(s.charCodeAt(i))
//     }
//     return Array.from(new Uint8Array(array))
// }

// export function arrayToString(array: number[]) {
//     var result = ''
//     for (var i = 0; i < array.length; i++) {
//         result += String.fromCharCode(array[i])
//     }
//     return result
// }

// export function arrayToBase64(array: number[]) {
//     return btoa(arrayToString(array))
// }

export async function sha256hexdigest(text: string) {
    // var array = new Uint8Array(await window.crypto.subtle.digest('SHA-256', encoder.encode(text)))
    // var result = ''
    // for (var i = 0; i < array.byteLength; i++) {
    //     result += array[i].toString(16).padStart(2, '0')
    // }
    // return result
    return CryptoJS.SHA256(CryptoJS.enc.Utf8.parse(text)).toString(CryptoJS.enc.Hex)
}
