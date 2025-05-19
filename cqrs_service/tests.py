from django.test import TestCase
from cqrs_service.aggregates import restore_aggregate, EnergyAggregate
from cqrs_service.models import Event, Snapshot

class AggregateRestoreTest(TestCase):

    def test_restore_aggregate(self):
        pet_id = "pet_123"

        # Создаём снапшот с ключом 'energy' (важно, чтобы совпадало с restore_state)
        # last_event_id = 0, чтобы применились все события с id > 0 (то есть все)
        Snapshot.objects.create(
            aggregate_id=pet_id,
            state={"energy": 10},  # Начальное состояние энергии из снапшота
            last_event_id=0  # Указываем 0, чтобы применились все события после него
        )

        # Создаём события с id автоматически увеличивающимся (обычно 1, 2 и т.д.)
        Event.objects.create(
            aggregate_id=pet_id,
            event_type="EnergyChargedEvent",
            payload={"pet_id": pet_id, "amount": 5},  # +5 энергии
        )
        Event.objects.create(
            aggregate_id=pet_id,
            event_type="EnergySpentEvent",
            payload={"pet_id": pet_id, "amount": 3},  # -3 энергии
        )

        # Восстанавливаем агрегат — сначала берём энергию из снапшота (10),
        # затем применяем события: +5 и -3 => итог 12
        aggregate = restore_aggregate(pet_id, EnergyAggregate)

        # Проверяем, что энергия агрегата равна ожидаемому значению
        self.assertEqual(aggregate.energy, 12)