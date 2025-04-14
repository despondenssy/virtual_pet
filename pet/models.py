from django.db import models
from django.utils import timezone

class Pet(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('playful', 'Playful'),
        ('sleepy', 'Sleepy'),
    ]
    
    name = models.CharField(max_length=50)  # Имя питомца
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='happy') # Настроение
    satiety = models.PositiveIntegerField(default=0)  # Голод (0-100)
    energy = models.PositiveIntegerField(default=100)  # Энергия (0-100)
    image = models.CharField(max_length=100, blank=True, null=True)

    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def update_state(self):
    # Получаем текущее время и время последнего обновления
        now = timezone.now()
        time_passed = now - self.last_updated
        minutes_passed = time_passed.total_seconds() // 60 

        if minutes_passed >= 2:  # Обновляем, если прошло хотя бы 2 минуты
            decay = int(minutes_passed)

            self.satiety = min(100, self.satiety + decay)
            self.energy = max(0, self.energy - decay)

            # Обновляем настроение на основе энергии и голода
            if self.energy < 30 or self.satiety > 70:
                self.mood = 'sad'
            elif self.energy > 70 and self.satiety < 30:
                self.mood = 'happy'
            else:
                self.mood = 'sleepy'

            self.last_updated = now
            self.save()

class PetAction(models.Model):
    pet = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='actions')
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pet.name} — {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"