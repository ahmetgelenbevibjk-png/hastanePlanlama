<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
// Eğer stores klasörünü 'src/stores' olarak oluşturduysanız:
import { useAuthStore } from '@/stores/auth.js';
// Eğer 'src/modules/Auth/store/authStore.js' olarak oluşturduysanız import yolunu ona göre güncelleyin.

const router = useRouter();
const authStore = useAuthStore();

const form = reactive({
  username: '',
  password: '',
});

const loading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';

  try {
    await authStore.login(form);
    // Giriş başarılı olunca çizelgeleme sayfasına yönlendir
    router.push('/schedule');
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail ||
      err.response?.data?.non_field_errors?.[0] ||
      'Giriş yapılamadı. Bilgilerinizi kontrol edin.';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
<div class="login-wrapper">
  <div class="login-card">
    <h2>Hastane Planlama Sistemi</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">KullanıcıAdı</label>
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
          {{ loading ? 'Giriş Yapılıyor...' : 'Giriş Yap' }}
      </button>
      <p v-if="errorMessage" class="error-message">{{errorMessage}}</p>
    </form>
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
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  text-align: center;
  color: #1e293b;
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
</style>