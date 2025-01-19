import { createStore } from 'vuex'

export const store = createStore({
  state() {
    return {
      tokenName: 'TokenB',
      token: localStorage.getItem('TokenB'),
      tsColorsName: 'tsColors',
      tsColors: JSON.parse(localStorage.getItem('tsColors')),
      prColorsName: 'prColors',
      prColors: JSON.parse(localStorage.getItem('prColors'))
    }
  },
  getters: {
    isAuthenticated: (state) => state.token != null
  },
  actions: {
    authenticateUser({ state, dispatch }, token) {
      localStorage.setItem(state.tokenName, token)
      state.token = token
      dispatch('colorSetup')
    },
    colorSetup({ state }) {
      state.tsColors = [
        { num: 1, color: '#0077d9' },
        { num: 2, color: '#0067bc' },
        { num: 3, color: '#0057a1' },
        { num: 4, color: '#004786' },
        { num: 5, color: '#00386c' },
        { num: 6, color: '#002a53' },
        { num: 7, color: '#001c3b' },
        { num: 8, color: '#001025' },
        { num: 9, color: '#000511' },
        { num: 10, color: '#000102' }
      ]
      localStorage.setItem(state.tsColorsName, JSON.stringify(state.tsColors))
      state.prColors = [
        { num: 1, color: '#d978b6' },
        { num: 2, color: '#e87699' },
        { num: 3, color: '#f67378' },
        { num: 4, color: '#f38e73' },
        { num: 5, color: '#eaac74' },
        { num: 6, color: '#dcc874' },
        { num: 7, color: '#cae373' },
        { num: 8, color: '#b3f979' },
        { num: 9, color: '#a6fa9b' },
        { num: 10, color: '#98fab9' }
      ]
      localStorage.setItem(state.prColorsName, JSON.stringify(state.prColors))
    },
    changeColorTs({ state }) {
      localStorage.setItem(state.tsColorsName, JSON.stringify(state.tsColors))
    },
    changeColorPr({ state }) {
      localStorage.setItem(state.prColorsName, JSON.stringify(state.prColors))
    },
    logout({ state }) {
      localStorage.removeItem(state.tokenName)
      state.token = null
    }
  }
})

export default store
