from django.db import models

class EntityView(models.Model):
    entity_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    value = models.IntegerField(default=0)

class EntityHistory(models.Model):
    entity_id = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)