from django.db import models

class Pet(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('playful', 'Playful'),
        ('sleepy', 'Sleepy'),
    ]
    
    name = models.CharField(max_length=50)  # Имя питомца
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='happy') # Настроение
    hunger = models.PositiveIntegerField(default=0)  # Голод (0-100)
    energy = models.PositiveIntegerField(default=100)  # Энергия (0-100)
    # image = models.ImageField(upload_to='pet_images/', blank=True, null=True)
    image = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name