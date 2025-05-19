from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from ..models import EnergyView, Event
from ..serializers import EnergyViewSerializer

class EnergyViewAPIView(APIView):
    @swagger_auto_schema(tags=['cqrs_query'])
    def get(self, request, pet_id):
        try:
            energy = EnergyView.objects.get(pet_id=pet_id)
        except EnergyView.DoesNotExist:
            return Response({'error': 'Pet energy not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyViewSerializer(energy)
        return Response(serializer.data)
    
class EnergyHistoryAPIView(APIView):
    @swagger_auto_schema(tags=['cqrs_query'])
    def get(self, request, pet_id):
        events = Event.objects.filter(aggregate_id=pet_id).order_by('timestamp')
        serialized = [{
            'event_type': e.event_type,
            'payload': e.payload,
            'timestamp': e.timestamp
        } for e in events]
        return Response(serialized)