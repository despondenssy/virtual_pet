from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from ..commands import ChargeEnergyCommand, SpendEnergyCommand
from ..aggregates import EnergyAggregate
from ..projections import EnergyProjection
from ..serializers import ChargeEnergySerializer, SpendEnergySerializer
from ..models import Event, Snapshot  # Модели для event sourcing

SNAPSHOT_THRESHOLD = 5  # порог количества событий для создания снапшота

def save_events_to_db(pet_id, events):
    objs = []
    last_event_id = None
    for event in events:
        obj = Event(
            aggregate_id=pet_id,
            event_type=type(event).__name__,
            payload=event.__dict__,  # сериализуем событие как словарь
        )
        objs.append(obj)
    Event.objects.bulk_create(objs)
    last_event_id = objs[-1].id if objs else None
    return last_event_id

def load_events_from_db(pet_id, from_event_id=None):
    qs = Event.objects.filter(aggregate_id=pet_id)
    if from_event_id:
        qs = qs.filter(id__gt=from_event_id)
    return qs.order_by('id')

def save_snapshot(pet_id, aggregate, last_event_id):
    state = aggregate.to_dict()
    Snapshot.objects.update_or_create(
        aggregate_id=pet_id,
        defaults={'state': state, 'last_event_id': last_event_id}
    )

class ChargeEnergyAPIView(APIView):

    @swagger_auto_schema(request_body=ChargeEnergySerializer, tags=['cqrs_command'])
    def post(self, request):
        serializer = ChargeEnergySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cmd = ChargeEnergyCommand(**serializer.validated_data)

        # Получаем последний снапшот
        snapshot = Snapshot.objects.filter(aggregate_id=cmd.pet_id).first()
        from_event_id = snapshot.last_event_id if snapshot else None

        # Загружаем события после снапшота
        events_qs = load_events_from_db(cmd.pet_id, from_event_id)
        events = [EnergyAggregate._deserialize_event(e) for e in events_qs]

        aggregate = EnergyAggregate(cmd.pet_id)
        aggregate.load(snapshot=snapshot, events=events)

        try:
            aggregate.handle_charge(cmd)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        last_event_id = save_events_to_db(cmd.pet_id, aggregate.changes)

        # Обновляем снапшот, если нужно
        if last_event_id and (len(aggregate.changes) >= SNAPSHOT_THRESHOLD):
            save_snapshot(cmd.pet_id, aggregate, last_event_id)

        for event in aggregate.changes:
            EnergyProjection.project(event)

        return Response({'message': 'Energy charged', 'new_energy': aggregate.energy})

class SpendEnergyAPIView(APIView):

    @swagger_auto_schema(request_body=SpendEnergySerializer, tags=['cqrs_command'])
    def post(self, request):
        serializer = SpendEnergySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cmd = SpendEnergyCommand(**serializer.validated_data)

        snapshot = Snapshot.objects.filter(aggregate_id=cmd.pet_id).first()
        from_event_id = snapshot.last_event_id if snapshot else None

        events_qs = load_events_from_db(cmd.pet_id, from_event_id)
        events = [EnergyAggregate._deserialize_event(e) for e in events_qs]

        aggregate = EnergyAggregate(cmd.pet_id)
        aggregate.load(snapshot=snapshot, events=events)

        try:
            aggregate.handle_spend(cmd)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        last_event_id = save_events_to_db(cmd.pet_id, aggregate.changes)

        if last_event_id and (len(aggregate.changes) >= SNAPSHOT_THRESHOLD):
            save_snapshot(cmd.pet_id, aggregate, last_event_id)

        for event in aggregate.changes:
            EnergyProjection.project(event)

        return Response({'message': 'Energy spent', 'new_energy': aggregate.energy})
