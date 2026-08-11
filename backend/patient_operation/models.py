from django.db import models
from base.models import BaseModel
from room.models import OperatingRoom
from surgeon.models import Surgeon
from anesthesia.models import AnesthesiaTeam  # Anestezi modelinizi import edin


class PatientOperation(BaseModel):
    class Priority(models.TextChoices):
        CRITICAL = 'CRITICAL', 'Kritik'
        HIGH = 'HIGH', 'Yüksek'
        MEDIUM = 'MEDIUM', 'Orta'
        LOW = 'LOW', 'Düşük'

    patient_name = models.CharField(max_length=100, verbose_name="Hasta Adı/Kodu")
    operation_name = models.CharField(max_length=100, verbose_name="Operasyon Adı")
    required_specialty = models.CharField(max_length=100, verbose_name="Gereken Uzmanlık")
    duration_slot = models.PositiveIntegerField(
        default=1,
        verbose_name="Süre (30dk Slot Sayısı)",
        help_text="Örn: 1 slot = 30 dk, 2 slot = 60 dk"
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Öncelik"
    )

    is_scheduled = models.BooleanField(
        default=False,
        verbose_name="Planlandı mı?"
    )

    # İlişkisel Alanlar (Foreign Keys)
    required_room = models.ForeignKey(
        OperatingRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Zorunlu Ameliyathane"
    )
    surgeon = models.ForeignKey(
        Surgeon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Atanan Cerrah"
    )
    anesthesia = models.ForeignKey(
        AnesthesiaTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Atanan Anestezi"
    )

    class Meta:
        verbose_name = "Hasta Ameliyat Operasyonu"
        verbose_name_plural = "Hasta Ameliyat Operasyonları"

    def __str__(self):
        return f"{self.patient_name} - {self.operation_name} ({self.get_priority_display()})"