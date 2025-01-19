import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.js'
import 'devextreme/dist/css/dx.light.css'
import axios from 'axios'

import { createApp } from 'vue'
import App from './App.vue'
import router from './plugins/router'
import store from './plugins/store'

axios.defaults.withCredentials = true
axios.defaults.baseURL = 'http://127.0.0.1:8000'

axios.interceptors.request.use(
  function (config) {
    config.headers.setAuthorization(`Bearer ${store.state.token}`)
    return config
  },
  function (error) {
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  function (response) {
    return response
  },
  function (error) {
    if (error) {
      if (error.response.status === 401) {
        store.dispatch('logout')
        return router.push('/login')
      }
      return Promise.reject(error)
    }
  }
)

const app = createApp(App)

app.use(router)
app.use(store)

app.mount('#app')
