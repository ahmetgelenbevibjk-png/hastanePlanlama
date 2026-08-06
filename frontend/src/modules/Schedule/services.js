import api from '@core/api';

export const ScheduleService={
    runScheduler(){
        return api.post('schedule/run/');
    },
    getRooms(){
        return api.get('rooms/');
    },
    getOperations(){
        return api.get('patient-operations/');
    },
}