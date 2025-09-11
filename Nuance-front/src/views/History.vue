<template>
  <div class="history">
    <div class="container">
      <div class="header">
        <button class="back-btn" @click="goBack">
          ← 返回首页
        </button>
        <h1>历史记录</h1>
        <div class="header-actions">
          <button class="clear-btn" @click="clearAllRecords" v-if="records.length > 0">
            清空记录
          </button>
        </div>
      </div>
      
      <div class="content">
        <div v-if="records.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h2>暂无记录</h2>
          <p>开始你的第一次情感书写之旅吧</p>
          <button class="start-writing-btn" @click="startWriting">
            开始书写
          </button>
        </div>
        
        <div v-else class="records-list">
          <div class="records-header">
            <h2>你的情感记录 ({{ records.length }})</h2>
            <div class="filter-options">
              <select v-model="selectedMoodFilter" class="mood-filter">
                <option value="">所有心情</option>
                <option v-for="mood in availableMoods" :key="mood.id" :value="mood.id">
                  {{ mood.emoji }} {{ mood.name }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="records-grid">
            <div 
              v-for="record in filteredRecords" 
              :key="record.id"
              class="record-card"
              :style="{ borderColor: getMoodTheme(record.mood).primary }"
              @click="viewRecord(record)"
            >
              <div class="record-header">
                <div class="mood-info">
                  <span class="mood-emoji">{{ getMoodData(record.mood).emoji }}</span>
                  <span class="mood-name">{{ getMoodData(record.mood).name }}</span>
                </div>
                <div class="record-date">{{ record.date }}</div>
              </div>
              
              <div class="record-preview">
                <h3>文章摘要</h3>
                <p>{{ getArticlePreview(record.article) }}</p>
              </div>
              
              <div class="record-footer">
                <div class="record-time">
                  {{ formatTime(record.timestamp) }}
                </div>
                <div class="record-actions">
                  <button 
                    class="view-btn"
                    :style="{ background: getMoodTheme(record.mood).primary }"
                    @click.stop="viewRecord(record)"
                  >
                    查看详情
                  </button>
                  <button 
                    class="delete-btn"
                    @click.stop="deleteRecord(record.id)"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HistoryPage',
  data() {
    return {
      records: [],
      selectedMoodFilter: '',
      moods: {
        happy: {
          name: '开心',
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
    availableMoods() {
      const usedMoods = [...new Set(this.records.map(r => r.mood))]
      return usedMoods.map(moodId => ({
        id: moodId,
        ...this.moods[moodId]
      }))
    },
    filteredRecords() {
      if (!this.selectedMoodFilter) {
        return this.records
      }
      return this.records.filter(record => record.mood === this.selectedMoodFilter)
    }
  },
  mounted() {
    this.loadRecords()
  },
  methods: {
    loadRecords() {
      const savedRecords = JSON.parse(localStorage.getItem('nuanceRecords') || '[]')
      this.records = savedRecords
    },
    
    getMoodData(moodId) {
      return this.moods[moodId] || this.moods.happy
    },
    
    getMoodTheme(moodId) {
      return this.getMoodData(moodId).theme
    },
    
    getArticlePreview(article) {
      if (!article) return '暂无文章内容'
      return article.length > 150 ? article.substring(0, 150) + '...' : article
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    viewRecord(record) {
      this.$router.push({
        name: 'ReportGeneration',
        query: {
          mood: record.mood,
          chatData: record.chatData,
          recordId: record.id
        }
      })
    },
    
    deleteRecord(recordId) {
      if (confirm('确定要删除这条记录吗？此操作不可恢复。')) {
        this.records = this.records.filter(record => record.id !== recordId)
        localStorage.setItem('nuanceRecords', JSON.stringify(this.records))
      }
    },
    
    clearAllRecords() {
      if (confirm('确定要清空所有记录吗？此操作不可恢复。')) {
        this.records = []
        localStorage.removeItem('nuanceRecords')
      }
    },
    
    startWriting() {
      this.$router.push('/mood-selection')
    },
    
    goBack() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.history {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  color: white;
}

.back-btn {
  background: rgba(255,255,255,0.1);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-2px);
}

.header h1 {
  font-size: 2.5rem;
  margin: 0;
  font-weight: 600;
  text-align: center;
  flex: 1;
}

.clear-btn {
  background: rgba(255,255,255,0.1);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.clear-btn:hover {
  background: rgba(255,0,0,0.3);
}

.content {
  min-height: 60vh;
}

.empty-state {
  text-align: center;
  color: white;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 30px;
}

.empty-state h2 {
  font-size: 2rem;
  margin: 0 0 15px 0;
  font-weight: 600;
}

.empty-state p {
  font-size: 1.2rem;
  opacity: 0.8;
  margin: 0 0 40px 0;
}

.start-writing-btn {
  background: rgba(255,255,255,0.9);
  color: #667eea;
  border: none;
  padding: 18px 40px;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.start-writing-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  color: white;
  flex-wrap: wrap;
  gap: 20px;
}

.records-header h2 {
  font-size: 1.8rem;
  margin: 0;
  font-weight: 600;
}

.mood-filter {
  background: rgba(255,255,255,0.1);
  color: white;
  border: 1px solid rgba(255,255,255,0.2);
  padding: 10px 15px;
  border-radius: 20px;
  font-size: 1rem;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.mood-filter option {
  background: #333;
  color: white;
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.record-card {
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  border: 3px solid transparent;
  color: #2c3e50;
}

.record-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mood-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 1.1rem;
}

.mood-emoji {
  font-size: 1.3rem;
}

.record-date {
  font-size: 0.9rem;
  opacity: 0.7;
  font-weight: 500;
}

.record-preview {
  margin-bottom: 20px;
}

.record-preview h3 {
  font-size: 1.1rem;
  margin: 0 0 10px 0;
  color: #444;
  font-weight: 600;
}

.record-preview p {
  color: #666;
  line-height: 1.5;
  margin: 0;
  font-size: 0.95rem;
}

.record-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid rgba(0,0,0,0.1);
}

.record-time {
  font-size: 0.85rem;
  color: #888;
}

.record-actions {
  display: flex;
  gap: 10px;
}

.view-btn, .delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn {
  color: white;
}

.delete-btn {
  background: rgba(255,0,0,0.1);
  color: #ff4757;
}

.view-btn:hover, .delete-btn:hover {
  transform: scale(1.05);
}

.delete-btn:hover {
  background: rgba(255,0,0,0.2);
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .records-grid {
    grid-template-columns: 1fr;
  }
  
  .records-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  
  .mood-filter {
    align-self: center;
    min-width: 200px;
  }
}

@media (max-width: 480px) {
  .record-card {
    padding: 20px;
  }
  
  .record-footer {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .record-actions {
    justify-content: center;
  }
}
</style>