import api from '@core/api'

export const operationService = {
  // Django urls.py tanımına göre 'operations/' veya 'operation/' olmalı
  getAll: () => api.get('operations/'),
  getById: (id) => api.get(`operations/${id}/`),
  create: (data) => api.post('operations/', data),
  update: (id, data) => api.put(`operations/${id}/`, data),
  delete: (id) => api.delete(`operations/${id}/`),
}