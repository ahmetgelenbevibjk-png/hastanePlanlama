from django.db import models

class BaseModel(models.Model):
    """Tüm modeller için ortak soyut temel sınıf."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        abstract = True