from rest_framework import serializers
from pet.models import Pet, PetAction

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ['id', 'name', 'mood', 'satiety', 'energy', 'image', 'last_updated']

class PetActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetAction
        fields = ['id', 'pet', 'action', 'timestamp']