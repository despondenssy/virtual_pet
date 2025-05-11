from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pet.models import PetAction
from .serializers import PetSerializer
from pet.utils import get_pet_from_cache, set_pet_to_cache

class PetInfoAPI(APIView):
    def get(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем состояние питомца
        pet.update_state()
        set_pet_to_cache(pet)  # сохраняем обновлённого питомца в кэш
        
        serializer = PetSerializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FeedPetAPI(APIView):
    def post(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика кормления
        pet.satiety = 100
        pet.energy -= 10
        pet.mood = 'happy'
        pet.save()

        PetAction.objects.create(pet=pet, action="Fed the pet")
        set_pet_to_cache(pet)

        return Response({"detail": "Pet fed successfully"}, status=status.HTTP_200_OK)

class PutToSleepAPI(APIView):
    def post(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика для сна питомца
        pet.energy = 100
        pet.mood = 'sleepy'
        pet.save()

        PetAction.objects.create(pet=pet, action="Put the pet to sleep")
        set_pet_to_cache(pet)

        return Response({"detail": "Pet put to sleep successfully"}, status=status.HTTP_200_OK)

class PlayWithPetAPI(APIView):
    def post(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика игры с питомцем
        pet.energy = max(pet.energy - 10, 0)
        pet.mood = "Playful"
        pet.save()

        PetAction.objects.create(pet=pet, action="Played with pet")
        set_pet_to_cache(pet)

        return Response({"detail": "Pet played with successfully"}, status=status.HTTP_200_OK)

class PetPetAPI(APIView):
    def post(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика поглаживания питомца
        pet.mood = "Happy"
        pet.save()

        PetAction.objects.create(pet=pet, action="Petted the pet")
        set_pet_to_cache(pet)

        return Response({"detail": "Pet petted successfully"}, status=status.HTTP_200_OK)