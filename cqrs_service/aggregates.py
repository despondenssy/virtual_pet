from .commands import ChargeEnergyCommand, SpendEnergyCommand
from .events import EnergyChargedEvent, EnergySpentEvent
from .models import Event  # для загрузки событий из БД
from .event_store import load_snapshot, load_events_db

class EnergyAggregate:
    def __init__(self, pet_id):
        self.pet_id = pet_id
        self.energy = 0
        self.changes = []  # накопленные события (event sourcing)

    # обработка команды "пополнить энергию"
    def handle_charge(self, command: ChargeEnergyCommand):
        if command.amount <= 0:
            raise ValueError("Amount to charge must be positive")
        event = EnergyChargedEvent(command.pet_id, command.amount)
        self.apply(event)
        self.changes.append(event)

    # обработка команды "потратить энергию"
    def handle_spend(self, command: SpendEnergyCommand):
        if command.amount <= 0:
            raise ValueError("Amount to spend must be positive")
        if command.amount > self.energy:
            raise ValueError("Not enough energy")
        event = EnergySpentEvent(command.pet_id, command.amount)
        self.apply(event)
        self.changes.append(event)

    # применение события к агрегату
    def apply(self, event):
        if isinstance(event, EnergyChargedEvent):
            self.energy += event.amount
        elif isinstance(event, EnergySpentEvent):
            self.energy -= event.amount

    # восстановление состояния из истории событий (event sourcing)
    def load_from_history(self, events):
        for event in events:
            self.apply(event)

    # Восстановление состояния из словаря (для снапшотов)
    def restore_state(self, state):
        self.energy = state.get('energy', state.get('current_energy', 0))

    # Представление текущего состояния агрегата как словаря (для снапшота)
    def to_dict(self):
        return {
            'energy': self.energy,
        }

    # Загрузка агрегата с учётом снапшота и событий после него
    def load(self, snapshot=None, events=None):
        """
        snapshot: объект снапшота или None
        events: список событий (могут быть объекты Event модели или уже десериализованные события)
        """
        if snapshot:
            self.restore_state(snapshot.state)
            events_to_apply = events or []
        else:
            events_to_apply = events or []

        # Преобразуем модели Event в объекты событий, если это модели Django
        deserialized_events = []
        for e in events_to_apply:
            if isinstance(e, Event):
                deserialized_events.append(self._deserialize_event(e))
            else:
                deserialized_events.append(e)

        self.load_from_history(deserialized_events)

    @staticmethod
    def _deserialize_event(event_model):
        """
        Преобразует модель Event из БД в объект события EnergyChargedEvent или EnergySpentEvent.
        """
        event_type = event_model.event_type
        data = event_model.payload

        if event_type == 'EnergyChargedEvent':
            return EnergyChargedEvent(data['pet_id'], data['amount'])
        elif event_type == 'EnergySpentEvent':
            return EnergySpentEvent(data['pet_id'], data['amount'])
        else:
            raise ValueError(f"Unknown event type: {event_type}")
        
    @classmethod
    def from_state(cls, state):
        obj = cls(state.get('pet_id', None))  # если нужен pet_id, иначе можно None
        obj.restore_state(state)
        return obj
    
    @staticmethod
    def event_from_record(event_type, event_data, aggregate_id=None):
        pet_id = event_data.get('pet_id', aggregate_id)
        if event_type == 'EnergyChargedEvent':
            return EnergyChargedEvent(pet_id, event_data['amount'])
        elif event_type == 'EnergySpentEvent':
            return EnergySpentEvent(pet_id, event_data['amount'])
        else:
            raise ValueError(f"Unknown event type: {event_type}")
        

def restore_aggregate(pet_id, aggregate_class):
    """
    Восстанавливает агрегат по id с помощью снапшота и последующих событий.
    
    aggregate_class — класс агрегата с методом apply(event)
    """
    snapshot = load_snapshot(pet_id)
    if snapshot:
        # Создаём агрегат из состояния снапшота
        aggregate = aggregate_class.from_state(snapshot.state)
        last_event_id = snapshot.last_event_id
    else:
        # Если снапшота нет, создаём пустой агрегат
        aggregate = aggregate_class()
        last_event_id = 0

    # Загружаем события после последнего снапшота
    events = load_events_db(pet_id)
    events_after_snapshot = [e for e in events if e.id > last_event_id]

    # Реплей событий
    for event_record in events_after_snapshot:
        event_data = event_record.payload
        event_type = event_record.event_type
        event = aggregate_class.event_from_record(event_type, event_data, event_record.aggregate_id)
        aggregate.apply(event)

    return aggregate