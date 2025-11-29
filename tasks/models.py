from django.db import models

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    importance = models.IntegerField(default=5)  # 1-10
    estimated_hours = models.FloatField(default=1.0)
    dependencies = models.JSONField(default=list, blank=True)
    last_score = models.IntegerField(default=0)
    last_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.title