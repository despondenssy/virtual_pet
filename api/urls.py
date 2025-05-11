from django.urls import path
from .views import (
    PetInfoAPI,
    FeedPetAPI,
    PutToSleepAPI,
    PlayWithPetAPI,
    PetPetAPI,
)

urlpatterns = [
    path('pet/<int:pet_id>/', PetInfoAPI.as_view(), name='pet_info_api'),
    path('pet/<int:pet_id>/feed/', FeedPetAPI.as_view(), name='feed_pet_api'),
    path('pet/<int:pet_id>/sleep/', PutToSleepAPI.as_view(), name='put_to_sleep_api'),
    path('pet/<int:pet_id>/play/', PlayWithPetAPI.as_view(), name='play_with_pet_api'),
    path('pet/<int:pet_id>/pet/', PetPetAPI.as_view(), name='pet_pet_api'),
]