<template>
  <div class="mood-selection" :style="{ background: currentTheme.background }">
    <div class="container">
      <div class="header">
        <button class="back-btn" @click="goBack" :style="{ color: currentTheme.text }">
          ← 返回/Back
        </button>
        <h1 :style="{ color: currentTheme.text }">How are you feeling today?</h1>
        <p :style="{ color: currentTheme.text, opacity: 0.8 }">
          让我们先从理解你的情绪开始
        </p>
      </div>
      
      <div class="mood-grid">
        <div 
          v-for="mood in moods" 
          :key="mood.id"
          class="mood-card"
          :class="{ active: selectedMood === mood.id }"
          :style="getMoodCardStyle(mood)"
          @click="selectMood(mood)"
        >
          <div class="mood-emoji">{{ mood.emoji }}</div>
          <!-- <div class="mood-name">{{ mood.name }}</div> -->
          <div>{{ mood.enName }}</div>
          <div class="mood-desc">{{ mood.enDesc }}</div>
        </div>
      </div>
      
      <div class="action-section" v-if="selectedMood">
        <button 
          class="continue-btn"
          :style="{ 
            background: currentTheme.primary, 
            color: currentTheme.buttonText 
          }"
          @click="continueToChat"
        >
          Continue
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MoodSelectionPage',
  data() {
    return {
      selectedMood: null,
      moods: [
        {
          id: 'happy',
          name: '开心',
          enName: 'Happy',
          emoji: '😊',
          description: '感到愉快和满足',
          enDesc: 'Feeling joyful and content',
          theme: {
            background: 'linear-gradient(135deg, #FFD93D 0%, #FF6B6B 100%)',
            primary: '#FF6B6B',
            text: '#2c3e50',
            buttonText: 'white'
          }
        },
        {
          id: 'sad',
          name: '悲伤',
          enName: 'Sad',
          emoji: '😢',
          description: '感到失落或难过',
          enDesc: 'Feeling down or upset',
          theme: {
            background: 'linear-gradient(135deg, #4A90E2 0%, #7B68EE 100%)',
            primary: '#7B68EE',
            text: 'white',
            buttonText: 'white'
          }
        },
        {
          id: 'excited',
          name: '兴奋',
          enName: 'Excited',
          emoji: '🤩',
          description: '充满活力和热情',
          enDesc: 'Full of energy and enthusiasm',
          theme: {
            background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)',
            primary: '#FF8E53',
            text: 'white',
            buttonText: 'white'
          }
        },
        {
          id: 'calm',
          name: '平静',
          enName: 'Calm',
          emoji: '😌',
          description: '内心宁静和放松',
          enDesc: 'Feeling peaceful and relaxed',
          theme: {
            background: 'linear-gradient(135deg, #A8E6CF 0%, #88D8C0 100%)',
            primary: '#88D8C0',
            text: '#2c3e50',
            buttonText: 'white'
          }
        },
        {
          id: 'angry',
          name: '愤怒',
          enName: 'Angry',
          emoji: '😠',
          description: '感到生气或烦躁',
          enDesc: 'Feeling angry or frustrated',
          theme: {
            background: 'linear-gradient(135deg, #FF6B6B 0%, #C44569 100%)',
            primary: '#C44569',
            text: 'white',
            buttonText: 'white'
          }
        },
        {
          id: 'anxious',
          name: '焦虑',
          enName: 'Anxious',
          emoji: '😰',
          description: '感到担心或不安',
          enDesc: 'Feeling worried or uneasy',
          theme: {
            background: 'linear-gradient(135deg, #FFA726 0%, #FF7043 100%)',
            primary: '#FF7043',
            text: 'white',
            buttonText: 'white'
          }
        }
      ]
    }
  },
  computed: {
    currentTheme() {
      if (this.selectedMood) {
        const mood = this.moods.find(m => m.id === this.selectedMood)
        return mood ? mood.theme : this.defaultTheme
      }
      return this.defaultTheme
    },
    defaultTheme() {
      return {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        primary: '#667eea',
        text: 'white',
        buttonText: 'white'
      }
    }
  },
  methods: {
    goBack() {
      this.$router.push('/')
    },
    selectMood(mood) {
      this.selectedMood = mood.id
    },
    getMoodCardStyle(mood) {
      const isSelected = this.selectedMood === mood.id
      return {
        background: isSelected ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.1)',
        color: isSelected ? '#2c3e50' : this.currentTheme.text,
        border: isSelected ? `3px solid ${this.currentTheme.primary}` : '2px solid rgba(255,255,255,0.2)',
        transform: isSelected ? 'scale(1.05)' : 'scale(1)'
      }
    },
    continueToChat() {
      if (this.selectedMood) {
        this.$router.push({
          name: 'ChatInterface',
          query: { mood: this.selectedMood }
        })
      }
    }
  }
}
</script>

<style scoped>
.mood-selection {
  min-height: 100vh;
  padding: 20px;
  transition: all 0.5s ease;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 50px;
  position: relative;
}

.back-btn {
  position: absolute;
  left: 0;
  top: 0;
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

.header h1 {
  font-size: 2.5rem;
  margin: 0 0 15px 0;
  font-weight: 600;
}

.header p {
  font-size: 1.2rem;
  margin: 0;
}

.mood-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.mood-card {
  padding: 30px 20px;
  border-radius: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255,255,255,0.2);
}

.mood-card:hover {
  transform: translateY(-5px) !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.mood-emoji {
  font-size: 3rem;
  margin-bottom: 15px;
}

.mood-name {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.mood-desc {
  font-size: 0.95rem;
  opacity: 0.8;
}

.action-section {
  text-align: center;
  margin-top: 40px;
}

.continue-btn {
  padding: 15px 40px;
  border: none;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

@media (max-width: 600px) {
  .mood-grid {
    grid-template-columns: 1fr;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .back-btn {
    position: static;
    margin-bottom: 20px;
  }
}
</style>