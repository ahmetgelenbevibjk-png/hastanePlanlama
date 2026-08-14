<script setup>
import {ref} from 'vue'
import {roomService} from '../services/roomService'

const props =defineProps({
  isOpen:{
    type:Boolean,
    default:false
  }
})

// Emits: Ana sayfaya kapatma veya başarıyla eklenme olaylarını bildiriyoruz
const emit = defineEmits(['close', 'created'])

const submitting = ref(false)
const newRoom = ref({
  name: '',
  specialty_type: ''
})

const close = () => {
  newRoom.value = { name: '', specialty_type: '' }
  emit('close')
}

const handleCreate = async () => {
  if (!newRoom.value.name.trim()) return

  submitting.value = true
  try {
    await roomService.create(newRoom.value)
    emit('created') // Ana sayfada listenin yenilenmesi için tetikliyoruz
    close()
  } catch (err) {
    alert('Salon eklenirken hata oluştu!')
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
<div v-if="isOpen" class="modal-backdrop" @click.self="close">
  <div class="modal-card">
    <div class="modal-header">
      <h3>➕ Yeni Salon Ekle</h3>
      <button class="btn-close" type="button" @click="close">✕</button>
    </div>

    <form @submit.prevent="handleCreate" class="styled-form">
      <div class="form-group">
        <label for="modalRoomName">Salon Adı / Kodu </label>
        <input
          id="modalRoomName"
          v-model="newRoom.name"
          type="text"
          placeholder="Örn:OR-2 veya Salon 1"
          required
          class="form-input"
          />
      </div>
      <div class="form-group">
          <label for="modalSpecialty">Özel Uzmanlık / Tipi (İsteğe Bağlı)</label>
          <input
            id="modalSpecialty"
            v-model="newRoom.specialty_type"
            type="text"
            placeholder="Örn: Kalp Anjiyo, Omurga vb."
            class="form-input"
          />
        </div>
      <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="close">
            İptal
          </button>
          <button type="submit" class="btn-primary" :disabled="submitting">
            <span v-if="submitting">Ekleniyor...</span>
            <span v-else>Salon Ekle</span>
          </button>
        </div>
    </form>
  </div>
</div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 18px;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.btn-close:hover {
  color: #0f172a;
}

.styled-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.form-input {
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>