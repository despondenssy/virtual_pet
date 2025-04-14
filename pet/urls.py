from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница питомцев
    path('add/', views.add_pet, name='add_pet'),  # Страница добавления питомца
    path('pet/<int:pet_id>/', views.pet_info, name='pet_info'),  # Страница просмотра и редактирования питомца
    path('feed_pet/<int:pet_id>/', views.feed_pet, name='feed_pet'),
    path('put_to_sleep/<int:pet_id>/', views.put_to_sleep, name='put_to_sleep'),
    path('delete/<int:pet_id>/', views.delete_pet, name='delete_pet'), # Удаление питомцев
]