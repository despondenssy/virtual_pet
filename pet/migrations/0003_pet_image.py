# Generated by Django 5.2 on 2025-04-05 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0002_pet_hunger_alter_pet_energy_alter_pet_mood'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='image',
            field=models.ImageField(default='pet_images/cat1.jpg', upload_to='pet_images/'),
        ),
    ]
