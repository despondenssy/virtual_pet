from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pet.models import Pet, PetAction
from .serializers import PetSerializer
from pet.utils import get_pet_from_cache, set_pet_to_cache, invalidate_pet_cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from messaging.producer import send_event

class PetInfoAPI(APIView):
    @swagger_auto_schema(responses={200: PetSerializer, 404: 'Pet not found'})
    def get(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем состояние питомца
        pet.update_state()
        set_pet_to_cache(pet)  # сохраняем обновлённого питомца в кэш
        
        serializer = PetSerializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CreatePetAPI(APIView):
    @swagger_auto_schema(request_body=PetSerializer, responses={201: PetSerializer})
    def post(self, request, format=None):
        serializer = PetSerializer(data=request.data)
        if serializer.is_valid():
            pet = serializer.save(mood='happy', satiety=75, energy=100)

            # Отправка события
            send_event(
                exchange_name='group3.21.direct',
                routing_key='group3.21.routing.key',
                message=f"Create: Pet {pet.id} — {pet.name}"
            )

            return Response(PetSerializer(pet).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeletePetAPI(APIView):
    @swagger_auto_schema(responses={204: 'Pet deleted successfully', 404: 'Pet not found'})
    def delete(self, request, pet_id, format=None):
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        invalidate_pet_cache(pet_id)

        # Отправка события
        send_event(
            exchange_name='group3.21.direct',
            routing_key='group3.21.routing.key',
            message=f"Delete: Pet {pet.id} — {pet.name}"
        )
        
        pet.delete()
        return Response({"detail": "Pet deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class FeedPetAPI(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'action': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ), responses={200: 'Pet fed successfully'})
    def post(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика кормления
        pet.satiety = 100
        pet.energy -= 10
        pet.mood = 'happy'
        pet.save()

        PetAction.objects.create(pet=pet, action=request.data.get('action', "Fed the pet"))
        set_pet_to_cache(pet)

        # Отправка события
        send_event(
            exchange_name='group3.21.direct',
            routing_key='group3.21.routing.key',
            message=f"Feed: Pet {pet.id} — {pet.name}"
        )

        return Response({"detail": "Pet fed successfully"}, status=status.HTTP_200_OK)

class PutToSleepAPI(APIView):
    @swagger_auto_schema(responses={200: 'Pet put to sleep successfully', 404: 'Pet not found'})
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

        # Отправка события
        send_event(
            exchange_name='group3.21.direct',
            routing_key='group3.21.routing.key',
            message=f"Sleep: Pet {pet.id} — {pet.name}"
        )

        return Response({"detail": "Pet put to sleep successfully"}, status=status.HTTP_200_OK)

class PlayWithPetAPI(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'action': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ), responses={200: 'Pet played with successfully', 404: 'Pet not found'})
    def post(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика игры с питомцем
        pet.energy = max(pet.energy - 10, 0)
        pet.mood = "Playful"
        pet.save()

        PetAction.objects.create(pet=pet, action=request.data.get('action', "Played with pet"))
        set_pet_to_cache(pet)

        # Отправка события
        send_event(
            exchange_name='group3.21.direct',
            routing_key='group3.21.routing.key',
            message=f"Play: Pet {pet.id} — {pet.name}"
        )

        return Response({"detail": "Pet played with successfully"}, status=status.HTTP_200_OK)

class PetPetAPI(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'action': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ), responses={200: 'Pet petted successfully', 404: 'Pet not found'})
    def post(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика поглаживания питомца
        pet.mood = "Happy"
        pet.save()

        PetAction.objects.create(pet=pet, action=request.data.get('action', "Petted the pet"))
        set_pet_to_cache(pet)

        # Отправка события
        send_event(
            exchange_name='group3.21.direct',
            routing_key='group3.21.routing.key',
            message=f"Pet: Pet {pet.id} — {pet.name}"
        )

        return Response({"detail": "Pet petted successfully"}, status=status.HTTP_200_OK)