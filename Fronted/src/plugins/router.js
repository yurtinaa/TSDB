import { createRouter, createWebHistory } from 'vue-router'
import PageNotFound from '@/views/PageNotFound.vue'
import Projects from '@/views/Projects.vue'
import SelectedProject from '@/views/SelectedProject.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import store from '@/plugins/store.js'

const routes = [
  {
    path: '/',
    name: 'Проекты',
    component: Projects,
    meta: {
      isNotAuth: true
    }
  },
  {
    path: '/project/:projectId&:name',
    component: SelectedProject,
    name: 'Проект',
    meta: {
      isNotAuth: true
    }
  },
  {
    path: '/login',
    component: LoginView,
    name: 'Авторизация',
    meta: {
      isNotAuth: false
    }
  },
  {
    path: '/register',
    component: RegisterView,
    name: 'Регистрация',
    meta: {
      isNotAuth: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    component: PageNotFound,
    name: 'Страница не найдена'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, _, next) => {
  if (to.matched.some((record) => record.meta.isNotAuth)) {
    if (store.getters.isAuthenticated) {
      next()
      return
    }
    next('/login')
  } else {
    if (store.getters.isAuthenticated) {
      next('/')
      return
    }
    next()
  }
})

export default router
