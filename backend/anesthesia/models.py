from django.db import models
from base.models import BaseModel

class AnesthesiaTeam(BaseModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="Ekip Adı")

    class Meta:
        verbose_name = "Anestezi Ekibi"
        verbose_name_plural = "Anestezi Ekipleri"
        ordering = ['name']

    def __str__(self):
        return self.name