import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import MoodSelection from '../views/MoodSelection.vue'
import ChatInterface from '../views/ChatInterface.vue'
import ReportGeneration from '../views/ReportGeneration.vue'
import History from '../views/History.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/mood-selection',
    name: 'MoodSelection',
    component: MoodSelection
  },
  {
    path: '/chat',
    name: 'ChatInterface',
    component: ChatInterface,
    props: route => ({ mood: route.query.mood })
  },
  {
    path: '/report',
    name: 'ReportGeneration',
    component: ReportGeneration,
    props: route => ({ 
      mood: route.query.mood,
      chatData: route.query.chatData,
      recordId: route.query.recordId 
    })
  },
  {
    path: '/history',
    name: 'History',
    component: History
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router