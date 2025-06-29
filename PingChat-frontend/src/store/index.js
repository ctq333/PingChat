// src/store/index.js
import { createStore } from 'vuex'

export default createStore({
  state: () => ({
    user: null,
    token: null,
  }),
  getters: {
    isLogin: state => !!state.token,
    isAdmin: state => state.user && state.user.is_admin,
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    SET_USER(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    LOGOUT(state) {
      state.token = null
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})