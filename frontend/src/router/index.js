import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Dashbaord from '../views/Dashboard.vue';
import Upload from '../components/UploadDocumnet.vue'
import Consent from '../components/ConsentPage.vue';
import Training from '../components/Training/TrainingDashboard.vue'
import Pop from '../components/Training/Pop.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/dashboard', name: 'Dashbaord', component: Dashbaord },
  { path: '/upload/:id', name: 'Upload', component: Upload },
  { path: '/consent/:id', name: 'Consent', component: Consent },
  { path: '/training', name: 'Training', component: Training },
  { path: '/phishing_test/:colleague_id', component: Pop },
  { path: '/study-material/:colleague_id', component: Pop, props: true},
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
