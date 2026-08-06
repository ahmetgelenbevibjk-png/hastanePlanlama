from django.db import models
from .base import BaseModel

class OperatingRoom(BaseModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="Oda Adı")
    specialty_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Özel Uzmanlık / Tipi"
    )

    class Meta:
        verbose_name = "Ameliyathane / Oda"
        verbose_name_plural = "Ameliyathaneler / Odalar"
        ordering = ['name']

    def __str__(self):
        return self.name