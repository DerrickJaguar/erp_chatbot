from django.db import models
from django.utils import timezone

class Lead(models.Model):
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now)
    conversation_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company}"