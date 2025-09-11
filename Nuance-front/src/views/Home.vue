<template>
  <div class="home">
    <div class="container">
      <div class="header">
        <h1 class="app-title">Nuance</h1>
        <p class="app-subtitle">AI英语学习与情感记录</p>
      </div>
      
      <div class="main-content">
        <div class="welcome-text">
          <h2>欢迎来到 Nuance</h2>
          <p>通过情感表达，提升英语能力</p>
        </div>
        
        <div class="action-buttons">
          <button 
            class="btn btn-primary" 
            @click="startWriting"
          >
            <span class="btn-icon">✏️</span>
            开始书写
          </button>
          
          <!-- <button 
            class="btn btn-secondary" 
            @click="viewHistory"
          >
            <span class="btn-icon">📚</span>
            查看历史
          </button> -->
        </div>
      </div>
      
      <div class="footer">
        <p>让情感成为学习的桥梁</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  methods: {
    startWriting() {
      this.$router.push('/mood-selection')
    },
    viewHistory() {
      this.$router.push('/history')
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.container {
  max-width: 500px;
  width: 100%;
  text-align: center;
  color: white;
}

.header {
  margin-bottom: 60px;
}

.app-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
  text-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.app-subtitle {
  font-size: 1.2rem;
  margin: 10px 0 0 0;
  opacity: 0.9;
  font-weight: 300;
}

.main-content {
  margin-bottom: 60px;
}

.welcome-text {
  margin-bottom: 50px;
}

.welcome-text h2 {
  font-size: 2rem;
  margin: 0 0 15px 0;
  font-weight: 500;
}

.welcome-text p {
  font-size: 1.1rem;
  opacity: 0.8;
  margin: 0;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.btn {
  width: 280px;
  padding: 18px 30px;
  border: none;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-decoration: none;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.btn-primary {
  background: rgba(255,255,255,0.95);
  color: #667eea;
}

.btn-primary:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.btn-secondary {
  background: rgba(255,255,255,0.15);
  color: white;
  border: 2px solid rgba(255,255,255,0.3);
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.25);
  border-color: rgba(255,255,255,0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.btn-icon {
  font-size: 1.3rem;
}

.footer {
  opacity: 0.7;
  font-size: 0.95rem;
  font-weight: 300;
}

@media (max-width: 600px) {
  .app-title {
    font-size: 2.8rem;
  }
  
  .btn {
    width: 100%;
    max-width: 280px;
  }
}
</style>