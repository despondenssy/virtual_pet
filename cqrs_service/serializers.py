from rest_framework import serializers

class ChargeEnergySerializer(serializers.Serializer):
    pet_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

class SpendEnergySerializer(serializers.Serializer):
    pet_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

class EnergyViewSerializer(serializers.Serializer):
    pet_id = serializers.IntegerField()
    current_energy = serializers.IntegerField()