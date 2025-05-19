from .models import EnergyView
from .events import EnergyChargedEvent, EnergySpentEvent

class EnergyProjection:

    @staticmethod
    def project(event):
        if isinstance(event, EnergyChargedEvent):
            obj, created = EnergyView.objects.get_or_create(pet_id=event.pet_id)
            obj.current_energy += event.amount
            obj.save()
        elif isinstance(event, EnergySpentEvent):
            obj, created = EnergyView.objects.get_or_create(pet_id=event.pet_id)
            obj.current_energy -= event.amount
            obj.save()