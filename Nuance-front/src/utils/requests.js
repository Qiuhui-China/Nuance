import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 30000,  // 30秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// ==================== 响应拦截器 ====================
api.interceptors.response.use(
  response => {
    const data = response.data || response
    
    // 处理业务逻辑错误
    if (data.error && data.error !== null) {
      const error = new Error(data.error)
      error.response = response
      throw error
    }
    
    // 调试日志（开发环境）
    if (process.env.NODE_ENV === 'development') {
      console.debug('API Response:', response.config.url, data)
    }
    
    return data
  },
  error => {
    // 统一错误格式
    if (error.response) {
      // 后端返回的错误
      const apiError = new Error(error.response.data?.error || 'API Error')
      apiError.status = error.response.status
      apiError.details = error.response.data
      throw apiError
    } else if (error.request) {
      // 请求已发出但无响应
      throw new Error('Network Error: No response received')
    } else {
      // 其他错误
      throw new Error(`Request Error: ${error.message}`)
    }
  }
)

// ==================== 会话API ====================
export const startSession = (sessionId, mood) => {
  return api.post('/start', {
    session_id: sessionId,
    mood: mood
  })
}

export const sendMessage = (sessionId, userInput) => {
  return api.post('/reply', {
    session_id: sessionId,
    user_input: userInput
  })
}

export const getHistory = (sessionId) => {
  return api.get(`/history/${sessionId}`)
}

export const endSession = (sessionId) => {
  return api.post(`/end/${sessionId}`)
}

// ==================== 文章润色API ====================
/**
 * 生成润色文章
 * @param {string} sessionId - 会话ID
 * @param {string} mood - 当前情绪状态
 * @returns {Promise<{article: string, word_count: number}>}
 */
export const generateArticle = async (sessionId, mood) => {
  try {
    console.log("sessionId", sessionId)
    console.log("mood", mood)

    const response = await api.post('/generate-article', {
      session_id: sessionId,
      mood: mood
    })
    
    return {
      article: response.article,
      wordCount: response.word_count,
      generatedAt: response.generated_at
    }
  } catch (error) {
    console.error('文章生成失败:', error)
    throw new Error(`文章生成失败: ${error.message}`)
  }
}
// ==================== 写作分析API ====================
/**
 * 分析用户写作并提供更正建议
 * @param {Array} conversationData - 对话数据数组，格式: [{type: 'ai'|'user', text: string, time: string}]
 * @returns {Promise<{corrections: Array, totalErrors: number}>}
 */
export const analyzeWritingWithData = (conversationData) => {
  return api.post('/analyze-writing', {
    conversation_data: conversationData
  })
}

/**
 * 通过sessionId分析历史记录的写作内容
 * @param {string} sessionId - 会话ID
 * @returns {Promise<{corrections: Array, totalErrors: number}>}
 */
export const analyzeWritingBySession = (sessionId) => {
  return api.post('/analyze-writing', {
    session_id: sessionId
  })
}
// ==================== 辅助方法 ====================
/**
 * 自动处理带重试的请求
 * @param {Function} requestFn - 返回Promise的请求函数
 * @param {number} retries - 重试次数 (默认3次)
 */
export const withRetry = (requestFn, retries = 3) => {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      requestFn()
        .then(resolve)
        .catch(error => {
          if (remaining > 0 && !error.response?.status) {
            console.warn(`Retrying... (${retries - remaining + 1}/${retries})`)
            setTimeout(() => attempt(remaining - 1), 1000)
          } else {
            reject(error)
          }
        })
    }
    attempt(retries)
  })
}