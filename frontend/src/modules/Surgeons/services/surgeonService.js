import api from '@core/api'

export const surgeonService = {
  getAll: () => api.get('surgeon/'),
  getById: (id) => api.get(`surgeon/${id}/`),
  create: (data) => api.post('surgeon/', data),
  update: (id, data) => api.put(`surgeon/${id}/`, data),
  delete: (id) => api.delete(`surgeon/${id}/`),
}