# Generated by Django 5.2 on 2025-04-05 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('mood', models.CharField(max_length=50)),
                ('energy', models.IntegerField(default=100)),
            ],
        ),
    ]
