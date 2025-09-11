const CHAT_PREFIX = 'chat_'
const ARTICLE_PREFIX = 'article_' // 新增文章存储前缀
const ANALYSIS_PREFIX = 'analysis_' // 新增分析报告存储前缀
export default {
  // 保存聊天记录 (保持不变)
  saveChat(sessionId, messages) {
    try {
      const data = {
        messages: messages,
        timestamp: Date.now(),
        expires: Date.now() + 24 * 60 * 60 * 1000 // 24小时过期
      }
      localStorage.setItem(CHAT_PREFIX + sessionId, JSON.stringify(data))
      return true
    } catch (error) {
      console.error('保存聊天记录失败:', error)
      return false
    }
  },

  // 新增：保存生成的文章
  saveArticle(sessionId, article) {
    try {
      const data = {
        article: article,
        generatedAt: Date.now(),
        expires: Date.now() + 7 * 24 * 60 * 60 * 1000 // 7天过期
      }
      localStorage.setItem(ARTICLE_PREFIX + sessionId, JSON.stringify(data))
      return true
    } catch (error) {
      console.error('保存文章失败:', error)
      return false
    }
  },

  // 获取聊天记录 (保持不变)
  getChat(sessionId) {
    const item = localStorage.getItem(CHAT_PREFIX + sessionId)
    if (!item) return null
    
    const data = JSON.parse(item)
    if (Date.now() > data.expires) {
      this.removeChat(sessionId)
      return null
    }
    return data.messages
  },

  // 新增：获取生成的文章
  getArticle(sessionId) {
    const item = localStorage.getItem(ARTICLE_PREFIX + sessionId)
    if (!item) return null
    
    const data = JSON.parse(item)
    if (Date.now() > data.expires) {
      this.removeArticle(sessionId)
      this.$message.error('文章已过期')
      return null
     
    }
    return data

  },

  // 删除聊天记录
  removeChat(sessionId) {
    localStorage.removeItem(CHAT_PREFIX + sessionId)
  },

  // 新增：删除文章
  removeArticle(sessionId) {
    localStorage.removeItem(ARTICLE_PREFIX + sessionId)
  },

  // 增强清理方法
  cleanup() {
    const now = Date.now()
    
    // 清理过期的聊天记录
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith(CHAT_PREFIX)) {
        try {
          const item = localStorage.getItem(key)
          if (item) {
            const data = JSON.parse(item)
            if (now > data.expires) {
              localStorage.removeItem(key)
            }
          }
        } catch (e) {
          console.warn('清理无效聊天记录:', key)
          localStorage.removeItem(key)
        }
      }
    })
    
    // 清理过期的文章
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith(ARTICLE_PREFIX)) {
        try {
          const item = localStorage.getItem(key)
          if (item) {
            const data = JSON.parse(item)
            if (now > data.expires) {
              localStorage.removeItem(key)
            }
          }
        } catch (e) {
          console.warn('清理无效文章:', key)
          localStorage.removeItem(key)
        }
      }
    })
  },

  // 新增：获取所有文章
  getAllArticles() {
    return Object.keys(localStorage)
      .filter(key => key.startsWith(ARTICLE_PREFIX))
      .map(key => {
        try {
          return {
            sessionId: key.replace(ARTICLE_PREFIX, ''),
            ...JSON.parse(localStorage.getItem(key))
          }
        } catch (e) {
          return null
        }
      })
      .filter(Boolean)
  },
 // 新增：保存分析报告
  saveAnalysis(sessionId, analysisData) {
    try {
      const data = {
        analysis: analysisData,
        analyzedAt: Date.now(),
        expires: Date.now() + 7 * 24 * 60 * 60 * 1000 // 7天过期
      }
      localStorage.setItem(ANALYSIS_PREFIX + sessionId, JSON.stringify(data))
      return true
    } catch (error) {
      console.error('保存分析报告失败:', error)
      return false
    }
  },
  // 新增：获取分析报告
  getAnalysis(sessionId) {
    const item = localStorage.getItem(ANALYSIS_PREFIX + sessionId)
    if (!item) return null
    
    const data = JSON.parse(item)
    if (Date.now() > data.expires) {
      this.removeAnalysis(sessionId)
      return null
    }
    return data.analysis
  },
  // 新增：删除分析报告
  removeAnalysis(sessionId) {
    localStorage.removeItem(ANALYSIS_PREFIX + sessionId)
  },
  // 新增：获取所有分析报告
  getAllAnalyses() {
    return Object.keys(localStorage)
      .filter(key => key.startsWith(ANALYSIS_PREFIX))
      .map(key => {
        try {
          return {
            sessionId: key.replace(ANALYSIS_PREFIX, ''),
            ...JSON.parse(localStorage.getItem(key))
          }
        } catch (e) {
          return null
        }
      })
      .filter(Boolean)
    }}