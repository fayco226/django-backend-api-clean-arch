from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True) # Username or email of the creator
    updated_by = models.CharField(max_length=255, null=True) # Username or email of the last updater

    class Meta:
        abstract = True
