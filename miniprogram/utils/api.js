/**
 * 河大家教小程序 — 统一 API 请求工具
 *
 * 封装：
 *  - 基础 URL（后续配置）
 *  - JWT Token 自动注入
 *  - 统一请求/响应处理
 *  - 分页数据解包
 *  - 错误提示
 */

// TODO: 替换为生产环境域名
const BASE_URL = 'https://api.heda-tutor.example.com'

// ============================================================
// 内部 helpers
// ============================================================

/**
 * 获取存储的 token
 */
function getToken() {
  try {
    return uni.getStorageSync('token') || ''
  } catch (e) {
    return ''
  }
}

/**
 * 发起请求
 * @param {string} method   — GET / POST / PUT / DELETE
 * @param {string} path     — 如 "/api/v1/teachers"
 * @param {object} data     — body / query 参数
 * @param {object} options  — { header, showLoading, loadingText }
 */
function request(method, path, data = null, options = {}) {
  const {
    header = {},
    showLoading = false,
    loadingText = '加载中...',
  } = options

  const token = getToken()
  const requestHeader = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...header,
  }

  if (showLoading) {
    uni.showLoading({ title: loadingText, mask: true })
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + path,
      method,
      header: requestHeader,
      data,
      success: (res) => {
        if (showLoading) uni.hideLoading()

        const statusCode = res.statusCode

        // 认证失效 — 跳转登录
        if (statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.removeStorageSync('role')
          uni.reLaunch({ url: '/pages/login/index' })
          reject(new Error('登录已过期'))
          return
        }

        if (statusCode >= 200 && statusCode < 300) {
          const body = res.data
          // 统一响应格式 { code: 0, message: "ok", data: ... }
          if (body && body.code === 0) {
            resolve(body)
          } else {
            const errMsg = (body && body.message) || '请求失败'
            uni.showToast({ title: errMsg, icon: 'none' })
            reject(new Error(errMsg))
          }
        } else {
          const errMsg = (res.data && res.data.message) || `服务器错误 (${statusCode})`
          uni.showToast({ title: errMsg, icon: 'none' })
          reject(new Error(errMsg))
        }
      },
      fail: (err) => {
        if (showLoading) uni.hideLoading()
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      },
    })
  })
}

// ============================================================
// 公开方法
// ============================================================

/**
 * GET 请求
 */
export function get(path, data = null, options = {}) {
  return request('GET', path, data, options)
}

/**
 * POST 请求
 */
export function post(path, data = null, options = {}) {
  return request('POST', path, data, options)
}

/**
 * PUT 请求
 */
export function put(path, data = null, options = {}) {
  return request('PUT', path, data, options)
}

/**
 * DELETE 请求
 */
export function del(path, data = null, options = {}) {
  return request('DELETE', path, data, options)
}

/**
 * 分页 GET — 自动解包 data.items
 * 返回 { items, total, page, page_size, total_pages }
 */
export async function getPaginated(path, params = {}, options = {}) {
  const res = await get(path, params, options)
  const pageData = res.data
  return {
    items: pageData.items || [],
    total: pageData.total || 0,
    page: pageData.page || 1,
    page_size: pageData.page_size || 20,
    total_pages: pageData.total_pages || 1,
  }
}

/**
 * 上传文件
 * @param {string} path  — 上传地址
 * @param {string} filePath — 本地文件路径
 * @param {string} name — 表单字段名
 */
export function uploadFile(path, filePath, name = 'file') {
  const token = getToken()
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: BASE_URL + path,
      filePath,
      name,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        try {
          const body = JSON.parse(res.data)
          if (body.code === 0) {
            resolve(body)
          } else {
            uni.showToast({ title: body.message || '上传失败', icon: 'none' })
            reject(new Error(body.message))
          }
        } catch (e) {
          reject(new Error('解析响应失败'))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      },
    })
  })
}

/**
 * 请求 API 并直接返回 res.data（不包含外层 {code,message}）
 * 适合需要直接拿到业务数据的场景
 */
export async function fetchData(path, params = {}, options = {}) {
  const res = await get(path, params, options)
  return res.data
}

/**
 * 提交并返回 data
 */
export async function postData(path, data = {}, options = {}) {
  const res = await post(path, data, options)
  return res.data
}

/**
 * 更新并返回 data
 */
export async function putData(path, data = {}, options = {}) {
  const res = await put(path, data, options)
  return res.data
}
