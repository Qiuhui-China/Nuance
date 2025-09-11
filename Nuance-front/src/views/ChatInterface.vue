<template>
  <div class="chat-interface" :style="{ background: moodTheme.background }">
    <div class="container">
      <div class="header">
        <button class="back-btn" @click="goBack" :style="{ color: moodTheme.text }">
          ← 返回
        </button>
        <div class="mood-indicator" :style="{ color: moodTheme.text }">
          <span class="mood-emoji">{{ currentMoodData.emoji }}</span>
          <span class="mood-name">{{ currentMoodData.enName }}</span>
           <!-- 新增轮数显示 -->
          <!-- <span class="turns-counter" v-if="turnsLeft >= 0">
            (剩余{{ turnsLeft }}轮)
          </span> -->
        </div>
      </div>
      
      <div class="chat-container">
        <div class="messages-area" ref="messagesArea" @mousewheel="handleScroll">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            class="message"
            :class="message.type"
          >
            <div class="message-content">
              <div class="message-text">{{ message.text }}</div>
              <div class="message-time">{{ message.time }}</div>
            </div>
          </div>
          
          <div v-if="isTyping" class="message ai typing">
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="input-area">
          <div class="input-container">
            <textarea
              v-model="currentMessage"
              @keydown.enter.prevent="send"
              placeholder="用中文或英文回答..."
              class="message-input"
              rows="1"
              ref="messageInput"
            ></textarea>
            <button 
              @click="send"
              :disabled="!currentMessage.trim() || isTyping"
              class="send-btn"
              :style="{ background: moodTheme.primary }"
            >
              发送
            </button>
          </div>
        </div>
        
        <div class="action-buttons" v-if="questionCount >= 2">
          <button 
            class="generate-report-btn"
            :style="{ 
              background: moodTheme.primary, 
              color: moodTheme.buttonText 
            }"
            @click="generateReport"
          >
            {{ chatCompleted ? '生成报告' : '提前生成报告' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  startSession, 
  sendMessage, 
  // endSession,
  // generateArticle
} from '@/utils/requests'
import storage from '@/utils/storage'

export default {
  name: 'ChatInterfacePage',
  props: {
    mood: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      
      messages: [],
      currentMessage: '',
      isTyping: false,
      isGenerating: false,
      chatCompleted: false,
      questionCount: 0,
      sessionId: '',
      turnsLeft: 8,
      moods: {
        happy: {
          name: '开心',
          enName: 'Happy',
          enDesc: 'Feeling happy and positive',
          emoji: '😊',
          theme: {
            background: 'linear-gradient(135deg, #FFD93D 0%, #FF6B6B 100%)',
            primary: '#FF6B6B',
            text: '#2c3e50',
            buttonText: 'white'
          }
        },
        sad: {
          name: '悲伤',
          enName: 'Sad',
          enDesc: 'Feeling down or upset',
          emoji: '😢',
          theme: {
            background: 'linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%)',
            primary: '#7B68EE',
            text: 'white',
            buttonText: 'white'
          }
        },
        excited: {
          name: '兴奋',
          enName: 'Excited',
          enDesc: 'Full of energy and enthusiasm',
          emoji: '🤩',
          theme: {
            background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)',
            primary: '#FF8E53',
            text: 'white',
            buttonText: 'white'
          }
        },
        calm: {
          name: '平静',
          enName: 'Calm',
          enDesc: 'Feeling peaceful and relaxed',
          emoji: '😌',
          theme: {
            background: 'linear-gradient(135deg, #A8E6CF 0%, #88D8C0 100%)',
            primary: '#88D8C0',
            text: '#2c3e50',
            buttonText: 'white'
          }
        },
        angry: {
          name: '愤怒',
          enName: 'Angry',
          enDesc: 'Feeling angry or frustrated',
          emoji: '😠',
          theme: {
            background: 'linear-gradient(135deg, #FF6B6B 0%, #C44569 100%)',
            primary: '#C44569',
            text: 'white',
            buttonText: 'white'
          }
        },
        anxious: {
          name: '焦虑',
          enName: 'Anxious',
          enDesc: 'Feeling worried or uneasy',
          emoji: '😰',
          theme: {
            background: 'linear-gradient(135deg, #FFA726 0%, #FF7043 100%)',
            primary: '#FF7043',
            text: 'white',
            buttonText: 'white'
          }
        }
      }
    }
  },
  computed: {
    currentMoodData() {
      return this.moods[this.mood] || this.moods.happy
    },
    moodTheme() {
      return this.currentMoodData.theme
    }
  },
  mounted() {
    this.sessionId = 'session_' + Date.now()
    this.initChat()
  },
  methods: {
    // 初始化对话
handleScroll() {
  const container = this.$refs.messagesArea
  // 实际使用这个变量，例如：
  const scrollPosition = container.scrollTop
  const containerHeight = container.clientHeight
  const scrollHeight = container.scrollHeight
  
  // 示例：检查是否滚动到顶部
  if (scrollPosition === 0) {
    console.log('滚动到顶部')
  }
  
  // 示例：检查是否接近底部
  if (scrollHeight - (scrollPosition + containerHeight) < 50) {
    console.log('接近底部')
  }
},
    
    // 修改scrollToBottom方法，添加平滑滚动
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesArea
        if (container) {
          container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
          })
        }
      })
    },
    async initChat() {
      try {
        this.isTyping = true
        setTimeout(() => {
              this.addAIMessage('Welcome to Nuance!')
        }, 2000);
    
        // this.addAIMessage('What steps are you taking right now to prepare for becoming an AI product manager?')
    //     // 第一轮：AI欢迎
    // this.addAIMessage("Hello! Welcome to Nuance! 👋");
    // this.addAIMessage("I see you're feeling " + this.currentMoodData.enName + " today. " + this.currentMoodData.emoji);

    // // 第二轮：用户回应
    // this.addUserMessage("Hi! Yes, I'm feeling " + this.currentMoodData.enName.toLowerCase() + " today.");

    // // 第三轮：AI提问
    // this.addAIMessage("That's interesting! Can you tell me more about what's making you feel this way?");

    // // 第四轮：用户详细描述
    // this.addUserMessage("I just got some good news about my career development, so I'm really excited!");

    // // 第五轮：AI深入探讨
    // this.addAIMessage("Congratulations! 🎉 That's wonderful news!");
    // this.addAIMessage("What specific aspects of this career development are you most excited about?");
        const response = await startSession(this.sessionId, this.mood)
        this.addAIMessage(response.response)
        this.turnsLeft = response.turns_left
      } catch (error) {
        this.handleError(error, '初始化对话')
      } finally {
        this.isTyping = false
      }
    },
 async send() {
    if (!this.currentMessage.trim() || this.isTyping) return
    
    try {
      // 保存原始消息
      const userMessage = this.currentMessage
      this.addUserMessage(userMessage)
      this.currentMessage = ''
      this.questionCount++
      
      this.isTyping = true
      
      // 确保只发送纯文本
      const response = await sendMessage(
        this.sessionId,
        this.sanitizeInput(userMessage)
      )
      
      this.addAIMessage(response.response)
      // 强制类型校验
     this.turnsLeft = Number(response.turns_left) || 0;
      // 处理会话结束
    if (response.ended_by === 'ai' || !response.session_active) {
      this.handleConversationEnd(response.ended_by || 'ai');
    }
    } catch (error) {
      this.handleError(error)
    } finally {
      this.isTyping = false
    }
  },
  sanitizeInput(input) {
    // 处理各种可能的输入类型
    if (typeof input === 'string') return input.trim()
    if (typeof input === 'object') {
      // 排除浏览器自动添加的事件属性
      const filtered = Object.fromEntries(
        Object.entries(input).filter(
          ([key]) => !['isTrusted', 'timestamp'].includes(key)
        )
      )
      return JSON.stringify(filtered)
    }
    return String(input)
  
  },
    // 处理对话结束
  handleConversationEnd(endedBy = 'ai') {
      this.chatCompleted = true
   
      const endMessages = {
        ai: '我已经收集了足够的信息，可以生成报告了',
        user: '您已结束对话',
        max_turns: '已达到最大对话轮次'
      }
      this.addAIMessage(endMessages[endedBy] || '对话已结束')
    },

    // 生成报告
async generateReport() {
  try {
    // 1. 尝试保存到LocalStorage
    storage.saveChat(this.sessionId, this.messages)
    
    if (!storage.getChat(this.sessionId)) {
      this.$message.error('保存对话记录失败')
      return 
      // throw new Error('保存对话记录失败，请重试')
    }

    // 2. 显示成功提示
    this.$message.success('保存成功，正在生成报告...')

    // 3. 短暂延迟后跳转（让用户看到提示）
    setTimeout(() => {
      this.$router.push({
        name: 'ReportGeneration',
        query: {
          sessionId: this.sessionId,
          mood: this.mood
        }
      })
    }, 1500) // 1.5秒后跳转

  } catch (error) {
    // 错误处理
    this.$notify({
      title: '操作失败',
      message: error.message || '发生未知错误',
      type: 'error',
      duration: 3000
    })
    
    console.error('生成报告失败:', error)
  }
},

    // 错误处理
    // 增强错误处理方法
  handleError(error, context = '操作') {
    console.error(`${context}失败:`, error)
    
    // 提取错误信息
    let errorMessage = error.message || '发生未知错误'
    const errorCode = error.code || 'UNKNOWN'
    
    // 特殊处理网络错误
    if (errorCode === 'NETWORK_ERROR') {
      errorMessage = '网络连接异常，请检查网络后重试'
    }
    
    // 添加带错误代码的提示
    this.addAIMessage(`系统提示: ${errorMessage} [错误代码: ${errorCode}]`)
    
    // 如果是网络错误，3秒后自动重试
    if (errorCode === 'NETWORK_ERROR') {
      setTimeout(() => {
        this.addAIMessage('正在尝试重新连接...')
        this.retryLastAction()
      }, 3000)
    }
  },
  
  // 重试机制
  retryLastAction() {
    const lastUserMessage = this.messages
      .filter(m => m.type === 'user')
      .pop()
    
    if (lastUserMessage) {
      this.sendMessage(lastUserMessage.text)
    }
  },

    // 添加消息辅助方法
    addAIMessage(text) {
      this.messages.push({
        type: 'ai',
        text: text,
        time: this.getCurrentTime()
      })
      this.scrollToBottom()
    },

    addUserMessage(text) {
      this.messages.push({
        type: 'user',
        text: text,
        time: this.getCurrentTime()
      })
      this.scrollToBottom()
    },

    // 工具方法
    getCurrentTime() {
      return new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },

    // scrollToBottom() {
    //   this.$nextTick(() => {
    //     const container = this.$refs.messagesArea
    //     if (container) container.scrollTop = container.scrollHeight
    //   })
    // },

    goBack() {
      this.$router.push('/mood-selection')
    }
  }
}
</script>

<style scoped>
.chat-interface {
min-height: 100vh;
  padding: 0;
  transition: all 0.5s ease;
  background: v-bind('moodTheme.background');
  background-attachment: fixed;
  background-size: cover;
  position: relative;
}

.container {
max-width: 800px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: transparent; /* 关键修改 */
}

.header {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
}

.back-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 10px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255,255,255,0.1);
}

.mood-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 600;
}

.mood-emoji {
  font-size: 1.5rem;
}

.chat-container {
  /* flex: 1; */
  display: flex;
  flex-direction: column;
  height:700px;
  padding: 0 20px 20px;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.3) transparent;
}

.messages-area::-webkit-scrollbar {
  width: 6px;
}

.messages-area::-webkit-scrollbar-track {
  background: transparent;
}

.messages-area::-webkit-scrollbar-thumb {
  background-color: rgba(255,255,255,0.3);
  border-radius: 3px;
}

.messages-area::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255,255,255,0.5);
}


.message {
  display: flex;
}

.message.ai {
  justify-content: flex-start;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  background: rgba(255,255,255,0.08); /* 降低不透明度 */
  backdrop-filter: blur(5px);
  border-radius: 18px;
  padding: 12px 18px;
  position: relative;
  border: 1px solid rgba(255,255,255,0.1); /* 添加细边框 */
}

.message.user .message-content {
  background: rgba(255,255,255,0.12); /* 用户消息稍亮一些 */
}

.message-text {
  color: white;
  line-height: 1.4;
  margin-bottom: 5px;
}

.message-time {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.6);
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: rgba(255,255,255,0.6);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.input-area {
  margin-top: auto;
}

.input-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 25px;
  padding: 10px 15px;
}

.message-input {
  flex: 1;
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  resize: none;
  outline: none;
  min-height: 20px;
  max-height: 100px;
}

.message-input::placeholder {
  color: rgba(255,255,255,0.6);
}

.send-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
}

.generate-report-btn {
  padding: 15px 30px;
  border: none;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.generate-report-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

@media (max-width: 600px) {
  .container {
    padding: 0 10px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
}

</style>