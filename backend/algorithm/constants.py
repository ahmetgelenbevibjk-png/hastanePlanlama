# Öncelik Puan Haritası
PRIORITY_WEIGHTS = {
    'KRITIK': 4,
    'CRITICAL': 4,
    'YÜKSEK': 3,
    'HIGH': 3,
    'NORMAL': 2,
    'MEDIUM': 2,
    'DÜŞÜK': 1,
    'LOW': 1,
}

# Zaman Parametreleri
DEFAULT_TOTAL_SLOTS = 20
SLOT_DURATION_MINUTES = 30
DEFAULT_DAY_NAME = 'Pazartesi'
DEFAULT_FALLBACK_DAY = 'Perşembe'

# Genel Ceza ve Skor Parametreleri
DEFAULT_UNASSIGNED_PENALTY = 35
DEFAULT_MAX_PENALTY_LIMIT = 100
ALTERNATIVE_MAX_PENALTY_LIMIT = 100
MAX_TOLERABLE_PENALTY = 100
HIGH_PRIORITY_THRESHOLD = 3
DEFAULT_NUM_CANDIDATES = 30

# Kural İhlal Ceza Ağırlıkları
PENALTY_SPECIALTY_MISMATCH = 20
PENALTY_ROOM_MISMATCH = 15
PENALTY_CRITICAL_DELAY_WEIGHT = 10
PENALTY_NORMAL_DELAY_WEIGHT = 3
PENALTY_REST_VIOLATION = 10  # Import hatasını çözen değişken
PENALTY_IDLE_SLOT = 1

# Strateji Konfigürasyonları
STRATEGY_CONFIGS = [
    {
        'name': 'Öncelik Odaklı (Standart)',
        'unassigned_penalty': 35,
        'penalty_multiplier': 1.0
    },
    {
        'name': 'Kritik Vaka Hassasiyeti',
        'unassigned_penalty': 35,
        'penalty_multiplier': 1.3
    },
    {
        'name': 'Salon Kapasite Verimliliği',
        'unassigned_penalty': 35,
        'penalty_multiplier': 0.8
    },
    {
        'name': 'Hızlı Sirkülasyon (Vaka Sayısı)',
        'unassigned_penalty': 35,
        'penalty_multiplier': 0.6
    },
    {
        'name': 'Dengeli Cerrah Programı',
        'unassigned_penalty': 35,
        'penalty_multiplier': 1.0
    }
]

# Ameliyathane - Branş Eşleştirmeleri
SPECIAL_ROOM_MAPPING = {
    'Genel Cerrahi': 'OR-1',
    'Kardiyoloji': 'OR-2',
    'Beyin Cerrahisi': 'OR-4',
    'Ortopedi': 'OR-3'
}

# Gün Haritalamaları (Türkçe -> İngilizce)
DAY_MAPPING = {
    'Pazartesi': 'monday',
    'Salı': 'tuesday',
    'Çarşamba': 'wednesday',
    'Perşembe': 'thursday',
    'Cuma': 'friday',
    'Cumartesi': 'saturday',
    'Pazar': 'sunday'
}

# İngilizce -> Türkçe Ters Gün Haritası
DAY_MAPPING_EN_TO_TR = {
    'monday': 'Pazartesi',
    'tuesday': 'Salı',
    'wednesday': 'Çarşamba',
    'thursday': 'Perşembe',
    'friday': 'Cuma',
    'saturday': 'Cumartesi',
    'sunday': 'Pazar'
}

# Sayısal İndeks -> Türkçe Gün Dönüşümü
DAYS_TR = [
    'Pazartesi',
    'Salı',
    'Çarşamba',
    'Perşembe',
    'Cuma',
    'Cumartesi',
    'Pazar'
]

# GA Parametreleri
GA_POPULATION_SIZE = 30
GA_GENERATIONS = 40
GA_MUTATION_RATE = 0.7
GA_TOURNAMENT_SIZE = 3
GA_ELITISM_RATE = 0.10