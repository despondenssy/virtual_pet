from .models import Event, Snapshot

SNAPSHOT_THRESHOLD = 10  # число событий для создания снапшота

def save_events_db(pet_id, events):
    for event in events:
        Event.objects.create(
            aggregate_id=pet_id,
            event_type=event['type'],
            payload=event['data']
        )

def load_events_db(pet_id):
    return list(Event.objects.filter(aggregate_id=pet_id).order_by('timestamp'))

def save_snapshot(pet_id, state, last_event_id):
    Snapshot.objects.update_or_create(
        aggregate_id=pet_id,
        defaults={
            'state': state,
            'last_event_id': last_event_id
        }
    )

def load_snapshot(pet_id):
    try:
        return Snapshot.objects.filter(aggregate_id=pet_id).order_by('-timestamp').first()
    except Snapshot.DoesNotExist:
        return None