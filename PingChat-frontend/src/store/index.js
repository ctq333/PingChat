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
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
    },
    LOGOUT(state) {
      state.user = null
      state.token = null
    }
  }
})