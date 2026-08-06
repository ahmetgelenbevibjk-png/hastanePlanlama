<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
// Eğer stores klasörünü 'src/stores' olarak oluşturduysanız:
import { useAuthStore } from '@/stores/auth.js';
// Eğer 'src/modules/Auth/store/authStore.js' olarak oluşturduysanız import yolunu ona göre güncelleyin.

const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
  username: '',
  password: '',
});

const isRegister = ref(false);
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// .env dosyasından API adresi okunuyor
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const toggleMode = () => {
  isRegister.value = !isRegister.value;
  errorMessage.value = '';
  successMessage.value = '';
  form.username = '';
  form.password = '';
};

const handleSubmit = async () => {
  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    if (isRegister.value) {
      // KAYIT OLMA İŞLEMİ
      const response = await axios.post(`${API_BASE_URL}/auth/register/`, form);
      successMessage.value = response.data.message || 'Kayıt başarılı! Admin onayından sonra giriş yapabilirsiniz.';

      // 2 saniye sonra otomatik giriş ekranına döndür
      setTimeout(() => {
        isRegister.value = false;
        successMessage.value = '';
      }, 2000);
    } else {
      // GİRİŞ YAPMA İŞLEMİ
      await authStore.login(form);
      router.push('/schedule');
    }
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data;
      if (data.detail) {
        errorMessage.value = data.detail;
      } else if (data.username) {
        errorMessage.value = `Kullanıcı adı hatası: ${data.username.join(' ')}`;
      } else if (data.password) {
        errorMessage.value = `Şifre hatası: ${data.password.join(' ')}`;
      } else if (data.error) {
        errorMessage.value = data.error;
      } else {
        errorMessage.value = 'Lütfen girdiğiniz bilgileri kontrol edin.';
      }
    } else {
      errorMessage.value = 'Sunucuya bağlanılamadı. Lütfen backend sunucusunu kontrol edin.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-wrapper">
    <div class="login-card">
      <h2>Hastane Planlama Sistemi</h2>
      <h3 class="auth-subtitle">{{ isRegister ? 'Kayıt Ol' : 'Giriş Yap' }}</h3>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">Kullanıcı Adı</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            placeholder="Kullanıcı adınızı girin"
          />
        </div>

        <div class="form-group">
          <label for="password">Şifre</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            placeholder="Şifrenizi girin"
          />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'İşleniyor...' : (isRegister ? 'Hesap Oluştur' : 'Giriş Yap') }}
        </button>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      </form>

      <div class="toggle-mode">
        <span @click="toggleMode">
          {{ isRegister ? 'Zaten hesabınız var mı? Giriş Yapın' : 'Hesabınız yok mu? Kayıt Olun' }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 85vh;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  background-color: #ffffff;
}

h2 {
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  text-align: center;
  color: #1e293b;
}

.auth-subtitle {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  text-align: center;
  color: #64748b;
  font-weight: 500;
}

.form-group {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.form-group input {
  padding: 0.65rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
}

.form-group input:focus {
  border-color: #2563eb;
}

button {
  width: 100%;
  padding: 0.75rem;
  margin-top: 0.5rem;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: #1d4ed8;
}

button:disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  color: #dc2626;
  font-size: 0.875rem;
  text-align: center;
}

.success-message {
  margin-top: 1rem;
  color: #16a34a;
  font-size: 0.875rem;
  text-align: center;
}

.toggle-mode {
  margin-top: 1.5rem;
  text-align: center;
}

.toggle-mode span {
  color: #2563eb;
  cursor: pointer;
  font-size: 0.875rem;
  text-decoration: underline;
  font-weight: 500;
}

.toggle-mode span:hover {
  color: #1d4ed8;
}
</style>