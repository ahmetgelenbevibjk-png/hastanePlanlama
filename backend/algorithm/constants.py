PRIORITY_WEIGHTS= {
    'KRITIK':4,
    'CRITICAL':4,
    'YÜKSEK':3,
    'HIGH':3,
    'NORMAL':2,
    'MEDIUM':2,
    'DÜŞÜK':1,
    'LOW':1,
}

DEFAULT_TOTAL_SLOTS=20
SLOT_DURATION_MINUTES=30
DEFAULT_DAY_NAME='Pazartesi'

#ceza ve skor parametreleri
DEFAULT_UNASSIGNED_PENALTY=50
DEFAULT_MAX_PENALTY_LIMIT=200
ALTERNATIVE_MAX_PENALTY_LIMIT=250
HIGH_PRIORITY_THRESHOLD=3
DEFAULT_NUM_CANDIDATES=5

#STRATEJİ AYARLARI
STRATEGY_CONFIGS=[
    {
        'name':'Öncelik Odaklı (Standart)',
        'unassigned_penalty':50,
        'penalty_multiplier':1.0
    },
    {
        'name':'Kritik Vaka Hassasiyeti',
        'unassigned_penalty':80,
        'penalty_multiplier':1.3
    },
    {
        'name':'Salon Kapasite Verimliliği',
        'unassigned_penalty':40,
        'penalty_multiplier':0.8
    },
    {
        'name': 'Hızlı Sirkülasyon (Vaka Sayısı)',
        'unassigned_penalty':30,
        'penalty_multiplier':0.6
    },
    {
        'name':'Dengeli Cerrah Programı',
        'unassigned_penalty':45,
        'penalty_multiplier':1.0
    }
]


#oda ve gün Haritalamaları
SPECIAL_ROOM_MAPPING= {
    'Genel Cerrahi':'OR-1',
    'Kardiyoloji':'OR-2',
    'Beyin Cerrahisi':'OR-4',
    'Ortopedi':'OR-3'
}

DAY_MAPPING= {
    'Pazartesi':'monday',
    'Salı':'tuesday',
    'Çarşamba':'wednesday',
'Perşembe': 'thursday',
    'Cuma': 'friday',
    'Cumartesi': 'saturday',
    'Pazar': 'sunday'
}


#Gün Dönüşümleri ve Varsayılan Gün

DAYS_TR= {
0: 'Pazartesi',
    1: 'Salı',
    2: 'Çarşamba',
    3: 'Perşembe',
    4: 'Cuma',
    5: 'Cumartesi',
    6: 'Pazar'
}

DEFAULT_FALLBACK_DAY='Perşembe'