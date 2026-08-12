import api from '@core/api';

export const ScheduleService = {
    runScheduler(dateStr) {
        return api.post('algorithm/run/', { date: dateStr });
    },

    getRooms() {
        return api.get('room/');
    },

    getOperations() {
        return api.get('patient-operation/');
    },
}