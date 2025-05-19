from django.db import models

class EnergyView(models.Model):
    pet_id = models.IntegerField(unique=True)
    current_energy = models.IntegerField(default=0)

    def __str__(self):
        return f"EnergyView(pet_id={self.pet_id}, energy={self.current_energy})"
    
class Event(models.Model):
    aggregate_id = models.CharField(max_length=100, db_index=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['aggregate_id', 'timestamp']),
        ]

    def __str__(self):
        return f"Event {self.event_type} for {self.aggregate_id} at {self.timestamp}"

class Snapshot(models.Model):
    aggregate_id = models.CharField(max_length=100, db_index=True, unique=True)
    state = models.JSONField()
    last_event_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Snapshot for {self.aggregate_id} at {self.timestamp}"