import logging
from django.core.cache import cache
from .models import Pet

logger = logging.getLogger(__name__)  # Создаём логгер

CACHE_TIMEOUT = 60 * 5  # 5 минут

# Получение питомца из кэша (или из БД, если кэш пуст)
def get_pet_from_cache(pet_id):
    key = f"pet:{pet_id}"
    pet = cache.get(key)
    if pet is None:
        logger.info(f"Cache MISS for pet_id={pet_id}")
        try:
            pet = Pet.objects.get(id=pet_id)
            set_pet_to_cache(pet)  # Кэшируем объект
        except Pet.DoesNotExist:
            return None
    else:
        logger.info(f"Cache HIT for pet_id={pet_id}")
    return pet

# Устанавливаем объект питомца в кэш
def set_pet_to_cache(pet):
    key = f"pet:{pet.id}"
    cache.set(key, pet, CACHE_TIMEOUT)
    # logger.info(f"Cache SET for pet_id={pet.id}")

# Удаление питомца из кэша
def invalidate_pet_cache(pet_id):
    key = f"pet:{pet_id}"
    cache.delete(key)
    logger.info(f"Cache DELETE for pet_id={pet_id}")