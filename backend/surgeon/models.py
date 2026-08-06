from django.db import models
from base.models import BaseModel

class Surgeon(BaseModel):
    DAYS_OF_WEEK = [
        ('monday', 'Pazartesi'),
        ('tuesday', 'Salı'),
        ('wednesday', 'Çarşamba'),
        ('thursday', 'Perşembe'),
        ('friday', 'Cuma'),
        ('saturday', 'Cumartesi'),
        ('sunday', 'Pazar'),
    ]

    name = models.CharField(max_length=100, verbose_name="Doktor Adı")
    specialty = models.CharField(max_length=100, verbose_name="Uzmanlık Alanı")
    off_day = models.CharField(
        max_length=20,
        choices=DAYS_OF_WEEK,
        blank=True,
        null=True,
        verbose_name="İzinli Gün"
    )

    class Meta:
        verbose_name = "Cerrah"
        verbose_name_plural = "Cerrahlar"

    def __str__(self):
        return f"{self.name} ({self.specialty})"