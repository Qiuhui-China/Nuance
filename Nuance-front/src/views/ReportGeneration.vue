<template>
  <div class="report-container" :style="{ background: moodTheme.theme.background }">
    <div class="report-header">
      <!-- <button class="back-btn" @click="goBack" :style="{ color: moodTheme.text }">
        ← 返回/back
      </button> -->
   
      <div class="mood-display" :style="{ color: moodTheme.text }">
        <span class="emoji">{{ currentMood.emoji }}</span>
        <span class="name">{{ currentMood.enName }}</span>
      </div>
   
    </div>

    <div class="report-content">
      <h1>Congratulations on finishing another English writing😊</h1>
      <br/>


      <!-- 临时批改建议 (模拟数据) -->
      <div class="correction-section">
        <h2>✏️ Here are some corrections you can make</h2>
         <div class="section-spinner" v-if="isLoadingCorrection">
          <div class="spinner" :style="{ borderTopColor: moodTheme.text }"></div>
          <div class="spinner-text" :style="{ color: moodTheme.text }">
            Please wait a second……
          </div>
        </div>
               <!-- 批改建议内容（加载完成/失败时显示） -->
        <div class="correction-grid" v-else>
          <div v-if="realCorrections.length">
          <div v-for="(item, index) in realCorrections" :key="index" class="correction-card">
              <div class="correction-type" 
            :style="{ backgroundColor: getTypeStyle(item.type).backgroundColor }">
              {{item.type}}
            </div >
            <div class="correction-type"
            :style="{ backgroundColor: getTypeStyle(item.type).backgroundColor }">
              {{ ERROR_TYPES[item.type]?.label }}
            </div>
             
            <div class="original-text">
              <label>原文:</label>
              <p>{{ item.original }}</p>
            </div>
            <div class="suggested-text">
              <label>建议:</label>
              <p>{{ item.suggestion }}</p>
            </div>
            <div class="explanation">
              {{ item.explanation }}
            </div>
            
          </div>
          </div>
            <!-- 加载失败：显示失败提示 -->
          <div v-else class="load-fail" :style="{ color: moodTheme.text }">
           ❌ Failed to load correction suggestions.
                     <button class="try-button" :style="{ background: moodTheme.theme.primary }" @click="tryGetCorrectionsAgain">try again</button>
          
          </div>

          
        </div>
      </div>
            <!-- 润色后的文章展示 -->
      <div class="polished-section">
        <h2>✨ This is an AI polished version of your essay</h2>
  <div class="section-spinner" v-if="isLoadingPolished">
    <div class="spinner" :style="{ borderTopColor: moodTheme.text }"></div>
    <div class="spinner-text" :style="{ color: moodTheme.text }">
      Please wait a second……
    </div>
  </div>
    <div v-else>
        <br>
         <p>Generated based on your conversation • {{ generationDate }}</p>
         <br/>
<div v-if="polishedArticle" class="article-meta">
  <span>{{ polishedArticle }}</span>
    <button class="copy-btn" @click="copyPolishedArticle">Copy</button>
  <br> 
</div>
<!-- 2. v-else 元素：与上方 v-if 直接相邻，控制“润色失败显示提示” -->
<div v-else class="load-fail" :style="{ color: moodTheme.text }">
 ❌ Failed to load AI polished version. Please try again.
  <button class="try-button" :style="{ background: moodTheme.theme.primary }" @click="tryGetPolishedArticleAgain">try again</button>
</div>

</div>


    </div>
  </div>
        <div class="action-buttons">
        <button class="share-btn" :style="{ background: moodTheme.theme.primary }" @click="saveReportAsImage">
          Save Report as PNG
        </button>
        <button class="home-btn" @click="goHome">
          Back to Home
        </button>
      </div>
  </div>
</template>

<script>
import html2canvas from 'html2canvas';
import { generateArticle,analyzeWritingBySession, analyzeWritingWithData } from '@/utils/requests'
import storage from '@/utils/storage'
import { ERROR_TYPES, SEVERITY_LEVELS } from '@/utils/data'

export default {
  
  name: 'SimplifiedReport',
  props: {
    mood: {
      type: String,
      required: true
    },
    sessionId: {
      type: String,
      required: true
    }
  },
  data() {
    return {

       // 新增：批改建议和AI润色的独立加载状态（初始为true，显示加载动画）
    isLoadingCorrection: true, 
    isLoadingPolished: true,
      ERROR_TYPES,
      polishedArticle: '',
      generationDate: new Date().toLocaleDateString('zh-CN'),
      originalMessages: [],
      isLoading: true,
      severityLevels: SEVERITY_LEVELS,
      realCorrections: [], // 替换掉mockCorrections
   
      typeColors: {
        vocabulary: '#4CAF50',
        grammar: '#FF9800',
        fluency: '#2196F3',
        structure: '#9C27B0'
      },
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
      },
      moodThemes: {
        happy: {
          name: '开心',
          emoji: '😊',
          background: 'linear-gradient(135deg, #FFD93D 0%, #FF6B6B 100%)',
          primary: '#FF6B6B',
          text: '#2c3e50'
        },
        sad: {
          name: '悲伤',
          emoji: '😢',
          background: 'linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%)',
          primary: '#7B68EE',
          text: 'white'
        }
        // 其他情绪主题...
      }
    }
  },
  computed: {
    currentMood() {
      return this.moods[this.mood] || this.moods.happy
    },
    moodTheme() {
      return this.currentMood
    }
  },
  methods: {
    copyPolishedArticle() {
    navigator.clipboard.writeText(this.polishedArticle).then(() => {
      this.$message.success('Copied successfully');
    }).catch(err => {
      console.error('Failed to copy: ', err);
      this.$message.error('Copy failed');
    });
  },
     saveReportAsImage() {
      console.log("save")
      const reportContainer = document.querySelector('.report-container');
      html2canvas(reportContainer).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = imgData;
        link.download = 'report.png';
        link.click();
        this.$message.success('报告已保存为图片');
      }).catch(error => {
        console.error('保存报告为图片失败：', error);
        this.$message.error('保存报告为图片失败，请重试');
      });
    },
      getTypeStyle(type) {
      return {
        backgroundColor: ERROR_TYPES[type]?.color || '#607D8B',
        color: 'white',
        borderRadius: '12px',
        padding: '2px 8px',
        fontSize: '0.8em'
      }
    },
    tryGetCorrectionsAgain() {
      console.log("tryGetCorrectionsAgain")
      
    this.isLoadingCorrection = true; // 显示加载动画
    const sessionId = this.$route.query.sessionId;
    this.realCorrections = []; // 清空原有批改数据

    analyzeWritingBySession(sessionId).then(data => {
      this.realCorrections = data.analysis.corrections;
      storage.saveAnalysis(sessionId, data);
      this.isLoadingCorrection = false;
      if (storage.getAnalysis(sessionId)) {
        this.$message.success('Correction suggestions loaded successfully');
      } else {
        this.$message.error('Failed to save correction suggestions');
      }
    }).catch(error => {
      this.isLoadingCorrection = false;
      const errorStr = error?.message?.toString() ?? '';
      if (errorStr.includes('No conversation history found')) {
        this.$message.warning('Server restart detected, trying to recover history from local storage...');
        analyzeWritingWithData(this.originalMessages).then(data => {
          this.realCorrections = data.analysis.corrections;
          storage.saveAnalysis(sessionId, data);
          this.isLoadingCorrection = false;
          if (storage.getAnalysis(sessionId)) {
            this.$message.success('Correction suggestions loaded successfully');
          } else {
            this.$message.error('Failed to save correction suggestions');
          }
        }).catch(retryError => {
          this.isLoadingCorrection = false;
          this.$message.error('Failed to load correction suggestions. Please try again later.',retryError);
        });
      } else {
        this.isLoadingCorrection = false;
        this.$message.error('Failed to load correction suggestions. Please try again later.');
      }
    });
  },
  tryGetPolishedArticleAgain() {
    this.isLoadingPolished = true; // 显示加载动画
    const sessionId = this.$route.query.sessionId;
    const mood = this.$route.query.mood;
    this.polishedArticle = ''; // 清空原有润色文章

    generateArticle(sessionId, mood).then(data => {
      this.polishedArticle = data.article;
      storage.saveArticle(sessionId, this.polishedArticle);
      this.isLoadingPolished = false;
      if (storage.getArticle(sessionId)) {
        this.$message.success('AI polished article loaded successfully');
      } else {
        this.$message.error('Failed to save AI polished article');
      }
    }).catch(error => {
      this.isLoadingPolished = false;
      this.$message.error('Failed to load AI polished article. Please try again later.',error);
    });
  },
    getFallbackArticle() {
      const fallbacks = {
        happy: `Today was an absolutely wonderful day! The sun was shining brightly...`,
        sad: `It's been a difficult time lately. I find myself reflecting on...`,
        angry: `I need to express my frustration about a situation that...`
      }
      return fallbacks[this.mood] || `This is a polished article based on your ${this.mood} mood conversation.`
    },
    goBack() {
      this.$router.go(-1)
    },
    goHome() {
      this.$router.push('/')
    }
  },
 async created() {
    // this.loadArticle()
    // 启动时清理过期数据
    storage.cleanup()
    
    const sessionId = this.$route.query.sessionId
    const mood = this.$route.query.mood
    // 从LocalStorage获取聊天记录
    this.originalMessages = storage.getChat(sessionId) || []
    const cache = storage.getArticle(sessionId) || ''
    const analysis_cache=storage.getAnalysis(sessionId)
    //文章生成
    if(cache){
      this.polishedArticle = cache.article
       this.isLoadingPolished = false; 
    }
    else{
      console.log('未缓存文章，正在生成...')
      this.$message.success('生成文章中...')
        generateArticle(sessionId, mood).then(data => {
        this.polishedArticle = data.article
        storage.saveArticle(sessionId, this.polishedArticle)
        if(storage.getArticle(sessionId)){
           this.$message.success('保存成功，正在生成报告...')
        }
        else{
          this.$message.error('保存失败')

        }
         this.isLoadingPolished = false;
      }) 

     
      // 使用后立即清理（可选）
      // storage.removeChat(sessionId)
    }
      if(analysis_cache){
      
        this.realCorrections=analysis_cache.analysis.corrections
        this.isLoadingCorrection=false
      }
      else{
 
        console.log("分析报告")
        this.$message.success('生成批改中')
        analyzeWritingBySession(sessionId).then(data => {
        console.log("分析报告成功",data)
          this.isLoadingCorrection = false; 
         this.realCorrections=data.analysis.corrections
         this.isLoadingCorrection=false;
           storage.saveAnalysis(sessionId,data)
            if(storage.getAnalysis(sessionId)){
              this.$message.success('保存批改成功')
            }
            else{
              this.$message.error('保存批改失败')
              
            }
      }).catch(error => {
        console.log('分析报告失败:', error)
          this.isLoadingCorrection = false; 
       // 使用可选链操作符和空值合并
  const errorStr = error?.message?.toString() ?? ''
  
  if (errorStr.includes('No conversation history found')) {
      this.$message.warning('检测到服务器重启，尝试从本地恢复历史...')
      
    
      analyzeWritingWithData(this.originalMessages).then(data=>{
            this.realCorrections=data.analysis.corrections
           
            storage.saveAnalysis(sessionId,data)
            if(storage.getAnalysis(sessionId)){
              this.$message.success('保存批改成功')
            }
            else{
              this.$message.error('保存批改失败')
            }
            
        })
        
        
      
      }
    }
  )
      }

  }
}
</script>

<style scoped>
.report-container {
  min-height: 100vh;
  padding: 20px;
  color: white;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  margin-bottom: 20px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 8px 15px;
  border-radius: 20px;
  transition: all 0.3s ease;
}
.copy-btn {

  /* color: white; */
  border: none;
  padding: 2px 10px;
  margin:5px;
  border-radius: 4px;
  cursor: poinster;
  margin-left: 10px;
}

.copy-btn:hover {
  background-color: gray;
}

.back-btn:hover {
  background: rgba(255,255,255,0.1);
}

.mood-display {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
}

.emoji {
  font-size: 1.5rem;
}

.report-content {
  display: flex;
  flex-direction: column;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.polished-section, 
.correction-section {
  background: rgba(255,255,255,0.1);
  border-radius: 15px;
  padding: 25px;
  margin-bottom: 30px;
  backdrop-filter: blur(5px);
}

h2 {
  margin-top: 0;
  font-size: 1.8rem;
}

.article-meta {
  opacity: 0.8;
  margin-bottom: 20px;
  font-size: 0.95rem;
}

.article-content pre {
  white-space: pre-wrap;
  font-family: inherit;
  line-height: 1.6;
  font-size: 1.05rem;
}

.correction-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr); 
  gap: 20px;
  margin-top: 20px;
  padding: 0 10px; /* 左右留少量内边距，避免卡片贴边 */
}

.correction-card {
  
  background: rgba(255,255,255,0.15);
  border-radius: 10px;
  padding: 20px;
  transition: all 0.3s ease;
  margin: 10px;
}

.correction-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.correction-type {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: bold;
  color: white;
  margin-left: 8px;
  margin-bottom: 15px;
}

.original-text, 
.suggested-text {
  margin: 15px 0;
}

label {
  display: block;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.explanation {
  font-size: 0.95rem;
  font-style: italic;
  opacity: 0.9;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.share-btn, 
.home-btn,
.try-button
{
  padding: 12px 25px;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.share-btn {
  color: white;

}
.try-button{
    margin: auto;
  width: 50%;
}

.home-btn {
  background: rgba(255,255,255,0.2);
  color: white;
}

.share-btn:hover, 
.home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

@media (max-width: 768px) {
  .report-content {
    padding: 15px;
  }
  
  .correction-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .share-btn, 
  .home-btn {
    width: 100%;
    max-width: 300px;
  }
}
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner-container {
  text-align: center;
  color: white;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto 15px;
}

.loading-text {
  font-size: 1.2rem;
  margin-top: 15px;
}

.blur-content {
  filter: blur(2px);
  opacity: 0.7;
  pointer-events: none;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
/* 让批改建议的失败提示占满网格宽度，居中显示 */
.correction-grid .load-fail {
  grid-column: 1 / -1; /* 跨所有列 */
  text-align: center;
  padding: 40px 0; /* 增加内边距，避免紧凑 */
}
</style>