export const TOTAL_DAILY_SLOTS=20 
export const SLOT_DURATION_MINUTES=30 
export const DEFAULT_OPERATION_DURATION = 60 
export const DEFAULT_SLOT_COUNT = 1
export const ROOM_CODE_PREFIX = 'OR-'

export const FITNESS_THRESHOLDS = {
    HIGH:80,
    MEDIUM:50
}

export const DEFAULT_LOCALE='tr-TR'

export const DEFAULT_PATIENT_NAME = 'Hasta'
export const DEFAULT_OPERATION_NAME = 'Ameliyat'
export const DEFAULT_SURGEON_NAME = '-'

export const MSG_UPDATE_SUCCESS = 'Ameliyat yeri başarıyla güncellendi.'
export const MSG_UPDATE_ERROR = 'Bu konuma taşıma yapılamaz!'

export const MANUAL_UPDATE_ENDPOINT = 'http://localhost:8000/api/algorithm/manual-update/'

export const TIME_SLOTS = [
  { index: 0, time: '08:00' }, { index: 1, time: '08:30' },
  { index: 2, time: '09:00' }, { index: 3, time: '09:30' },
  { index: 4, time: '10:00' }, { index: 5, time: '10:30' },
  { index: 6, time: '11:00' }, { index: 7, time: '11:30' },
  { index: 8, time: '12:00' }, { index: 9, time: '12:30' },
  { index: 10, time: '13:00' }, { index: 11, time: '13:30' },
  { index: 12, time: '14:00' }, { index: 13, time: '14:30' },
  { index: 14, time: '15:00' }, { index: 15, time: '15:30' },
  { index: 16, time: '16:00' }, { index: 17, time: '16:30' },
  { index: 18, time: '17:00' }, { index: 19, time: '17:30' }
]

export const MOCK_ROOMS = [
  { id: 1, name: 'OR-1 (Genel Cerrahi)' },
  { id: 2, name: 'OR-2 (Kardiyoloji)' },
  { id: 3, name: 'OR-3 (Ortopedi)' },
  { id: 4, name: 'OR-4 (Beyin Cerrahisi)' }
]

export const MOCK_OPERATIONS = [
    {
        id:101,
        operation_name:'Apendektomi',
        surgeon_name:'Dr. Ahmet',
        duration_slot:2,
        room_id:1,
        start_slot:2
    }
]