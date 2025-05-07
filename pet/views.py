from .utils import get_pet_from_cache, set_pet_to_cache, invalidate_pet_cache
from django.shortcuts import render, redirect, get_object_or_404
from .models import Pet
from .forms import PetForm
from .forms import RenamePetForm
from .models import PetAction

# Домашняя страница
def home(request):
    pets = Pet.objects.all()
    return render(request, 'pet/home.html', {'pets': pets})


# Просмотр и редактирование информации о питомце
def pet_info(request, pet_id):
    pet = get_pet_from_cache(pet_id)
    if not pet:
        return redirect('home')
    
    pet.update_state()
    set_pet_to_cache(pet)  # сохраняем обновлённого питомца в кэш

    if request.method == 'POST':
        form = RenamePetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            set_pet_to_cache(pet)  # снова сохранить после переименования
            return redirect('pet_info', pet_id=pet.id)
    else:
        form = RenamePetForm(instance=pet)

    return render(request, 'pet/pet_info.html', {'pet': pet, 'form': form})

# Добавление питомца
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.mood = 'happy'
            pet.satiety = 75
            pet.energy = 100
            pet.save()
            return redirect('home')
    else:
        form = PetForm()

    return render(request, 'pet/add_pet.html', {'form': form})

# Удаление питомцев
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        invalidate_pet_cache(pet_id)
        pet.delete()
        return redirect('home')
    return render(request, 'pet/delete_pet.html', {'pet': pet})

# Кормление
def feed_pet(request, pet_id):
    pet = get_pet_from_cache(pet_id)
    if not pet:
        return redirect('home')

    pet.satiety = 100
    pet.energy -= 10
    pet.mood = 'happy'
    pet.save()

    PetAction.objects.create(pet=pet, action="Fed the pet")
    set_pet_to_cache(pet)

    return redirect('pet_info', pet_id=pet.id)

# Сон
def put_to_sleep(request, pet_id):
    pet = get_pet_from_cache(pet_id)
    if not pet:
        return redirect('home')

    pet.energy = 100
    pet.mood = 'sleepy'
    pet.save()

    PetAction.objects.create(pet=pet, action="Put the pet to sleep")
    set_pet_to_cache(pet)

    return redirect('pet_info', pet_id=pet.id)

# Поиграть
def play_with_pet(request, pet_id):
    pet = get_pet_from_cache(pet_id)
    if not pet:
        return redirect('home')

    pet.energy = max(pet.energy - 10, 0)
    pet.mood = "Playful"
    pet.save()

    PetAction.objects.create(pet=pet, action="Played with pet")
    set_pet_to_cache(pet)

    return redirect('pet_info', pet_id=pet.id)

# Погладить
def pet_pet(request, pet_id):
    pet = get_pet_from_cache(pet_id)
    if not pet:
        return redirect('home')

    pet.mood = "Happy"
    pet.save()

    PetAction.objects.create(pet=pet, action="Petted the pet")
    set_pet_to_cache(pet)

    return redirect('pet_info', pet_id=pet.id)