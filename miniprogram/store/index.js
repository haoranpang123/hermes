/**
 * 河大家教小程序 — 全局状态管理（Store）
 *
 * 基于 Vue.observable 的轻量状态管理，无需引入 Vuex。
 * 替代 App.globalData，提供响应式能力。
 */

import Vue from 'vue'

// ============================================================
// 根 Store — 聚合所有模块
// ============================================================

const store = Vue.observable({
  // ---- 用户状态 ----
  user: {
    token: '',
    userInfo: null,       // { user_id, nickname, avatar_url, phone, role }
    role: '',             // '' | 'parent' | 'teacher'
    isLogin: false,
  },

  // ---- 钱包状态（家长端） ----
  wallet: {
    balance: 0,
    total_recharged: 0,
    total_spent: 0,
  },
})

// ============================================================
// 用户模块 actions
// ============================================================

/** 从本地存储恢复登录状态 */
export function restoreLogin() {
  try {
    const token = uni.getStorageSync('token') || ''
    const userInfo = uni.getStorageSync('userInfo') || null
    const role = uni.getStorageSync('role') || ''

    if (token && userInfo) {
      store.user.token = token
      store.user.userInfo = userInfo
      store.user.role = role
      store.user.isLogin = true
      return true
    }
  } catch (e) {
    // ignore
  }
  return false
}

/** 保存登录信息 */
export function saveLogin(token, userInfo, role) {
  store.user.token = token
  store.user.userInfo = userInfo
  store.user.role = role
  store.user.isLogin = true

  uni.setStorageSync('token', token)
  uni.setStorageSync('userInfo', userInfo)
  uni.setStorageSync('role', role)
}

/** 清除登录信息 */
export function clearLogin() {
  store.user.token = ''
  store.user.userInfo = null
  store.user.role = ''
  store.user.isLogin = false

  uni.removeStorageSync('token')
  uni.removeStorageSync('userInfo')
  uni.removeStorageSync('role')
}

/** 更新用户信息 */
export function updateUserInfo(userInfo) {
  store.user.userInfo = { ...store.user.userInfo, ...userInfo }
  uni.setStorageSync('userInfo', store.user.userInfo)
}

// ============================================================
// 钱包模块 actions
// ============================================================

/** 更新钱包余额 */
export function updateWallet(walletData) {
  if (walletData) {
    store.wallet.balance = walletData.balance || 0
    store.wallet.total_recharged = walletData.total_recharged || 0
    store.wallet.total_spent = walletData.total_spent || 0
  }
}

// ============================================================
// 便捷导出
// ============================================================

/** 获取当前 token */
export function getToken() {
  return store.user.token || uni.getStorageSync('token') || ''
}

/** 获取当前用户 */
export function getUser() {
  return store.user.userInfo
}

/** 获取当前角色 */
export function getRole() {
  return store.user.role || uni.getStorageSync('role') || ''
}

/** 是否已登录 */
export function isLogin() {
  return store.user.isLogin
}

export default store
