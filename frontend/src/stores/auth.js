import {defineStore} from 'pinia';
import api from '@/@core/api';

export const useAuthStore= defineStore('auth', {
    state: ()=> ({
        token:localStorage.getItem('token')|| null,
        user:JSON.parse(localStorage.getItem('user')) || null,
    }),
    getters:{
        isAuthenticated:(state)=> !!state.token,
    },
    actions:{
        async login (credenticials) {
            try {
                const response =await api.post('auth/login/',credenticials);
                this.token = response.data.access || response.data.token;
        this.user = response.data.user || null;

        localStorage.setItem('token', this.token);
        if (this.user) {
          localStorage.setItem('user', JSON.stringify(this.user));
        }

        return response.data;
      } catch (error) {
        console.error('Giriş başarısız:', error);
        throw error;
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
            }
        }
    
})