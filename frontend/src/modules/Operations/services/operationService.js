import api from '@core/api'

export const operationService= {
    getAll:()=> api.get('patient_operation/'),
    getById:(id)=>api.get(`patient_operation/${id}`),
    create:(data)=>api.post(`patient_operation/`,data),
    update: (id, data) => api.put(`patient_operation/${id}/`, data),
    delete:(id)=>api.delete(`patient_operation/${id}`),
}