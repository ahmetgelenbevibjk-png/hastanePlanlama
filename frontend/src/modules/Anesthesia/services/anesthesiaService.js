import api from '@core/api'

export const anesthesiaService = {
  getAll: () => api.get('anesthesia/'),
  getById: (id) => api.get(`anesthesia/${id}/`),
  create: (data) => api.post('anesthesia/', data),
  update: (id, data) => api.put(`anesthesia/${id}/`, data),
  delete: (id) => api.delete(`anesthesia/${id}/`),
}