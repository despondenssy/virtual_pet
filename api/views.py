from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pet.models import Pet, PetAction
from .serializers import PetSerializer
from pet.utils import get_pet_from_cache, set_pet_to_cache, invalidate_pet_cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from messaging.producer import send_event
from prometheus_client import Counter, Gauge, Summary, generate_latest
from django.http import HttpResponse
import time

# Метрики Prometheus
# Общее количество действий над питомцами
pet_action_counter = Counter(
    'pet_actions_total',
    'Total number of actions performed on pets',
    ['action_type', 'pet_name']
)

# Метрика уровня энергии
pet_energy_level = Gauge(
    'pet_energy_level',
    'Current energy level of the pet',
    ['pet_name']
)

# Время обработки API-запроса взаимодействий
action_duration_summary = Summary(
    'pet_action_duration_seconds',
    'Time taken to perform pet actions',
    ['action_type']
)

MOOD_MAP = {
    'happy': 3,
    'playful': 2,
    'sleepy': 1,
    'neutral': 0,
    'sad': -1
}

class PetInfoAPI(APIView):
    @swagger_auto_schema(responses={200: PetSerializer, 404: 'Pet not found'})
    def get(self, request, pet_id, format=None):
        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем состояние питомца
        pet.update_state()
        set_pet_to_cache(pet)

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
        start_time = time.time()

        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика кормления
        pet.satiety = 100
        pet.energy = max(pet.energy - 10, 0)  # например, кормим — энергия чуть падает
        pet.mood = 'happy'
        pet.save()

        action = request.data.get('action', "Fed the pet")
        PetAction.objects.create(pet=pet, action=action)
        set_pet_to_cache(pet)

        pet_action_counter.labels(action_type="feed", pet_name=pet.name).inc()
        pet_energy_level.labels(pet_name=pet.name).set(pet.energy)
        action_duration_summary.labels(action_type="feed").observe(time.time() - start_time)

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
        start_time = time.time()

        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика для сна питомца
        pet.energy = 100
        pet.mood = 'sleepy'
        pet.save()

        PetAction.objects.create(pet=pet, action="Put the pet to sleep")
        set_pet_to_cache(pet)

        pet_action_counter.labels(action_type="sleep", pet_name=pet.name).inc()
        pet_energy_level.labels(pet_name=pet.name).set(pet.energy)
        action_duration_summary.labels(action_type="sleep").observe(time.time() - start_time)

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
        start_time = time.time()

        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика игры с питомцем
        pet.energy = max(pet.energy - 10, 0)
        pet.mood = "playful"
        pet.save()

        action = request.data.get('action', "Played with pet")
        PetAction.objects.create(pet=pet, action=action)
        set_pet_to_cache(pet)

        pet_action_counter.labels(action_type="play", pet_name=pet.name).inc()
        pet_energy_level.labels(pet_name=pet.name).set(pet.energy)
        action_duration_summary.labels(action_type="play").observe(time.time() - start_time)

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
        start_time = time.time()

        pet = get_pet_from_cache(pet_id)
        if not pet:
            return Response({"detail": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Логика поглаживания питомца
        pet.mood = "happy"
        pet.save()

        action = request.data.get('action', "Petted the pet")
        PetAction.objects.create(pet=pet, action=action)
        set_pet_to_cache(pet)

        pet_action_counter.labels(action_type="pet", pet_name=pet.name).inc()
        pet_energy_level.labels(pet_name=pet.name).set(pet.energy)
        action_duration_summary.labels(action_type="pet").observe(time.time() - start_time)

        # Отправка события
        send_event(
            exchange_name='group3.21.direct',
            routing_key='group3.21.routing.key',
            message=f"Pet: Pet {pet.id} — {pet.name}"
        )

        return Response({"detail": "Pet petted successfully"}, status=status.HTTP_200_OK)

class PetMetricsAPI(APIView):
    def get(self, request, format=None):
        return HttpResponse(generate_latest(), content_type="text/plain")