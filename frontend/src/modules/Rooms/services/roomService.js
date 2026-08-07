import api from '@core/api'

export const roomService = {
  getAll: () => api.get('room/'),
  getById: (id) => api.get(`room/${id}/`),
  create: (data) => api.post('room/', data), // 'room/' sonunda slash olmalı
  update: (id, data) => api.put(`room/${id}/`, data),
  delete: (id) => api.delete(`room/${id}/`),
}