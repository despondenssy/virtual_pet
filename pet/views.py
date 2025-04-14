from django.shortcuts import render, redirect, get_object_or_404
from .models import Pet
from .forms import PetForm
from .forms import RenamePetForm

# Домашняя страница
def home(request):
    pets = Pet.objects.all()
    return render(request, 'pet/home.html', {'pets': pets})


# Просмотр и редактирование информации о питомце
def pet_info(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == 'POST':
        form = RenamePetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
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
            pet.hunger = 0
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
        pet.delete() 
        return redirect('home')
    return render(request, 'pet/delete_pet.html', {'pet': pet})

# Кормление
def feed_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    pet.hunger = 100
    pet.energy -= 10
    pet.mood = 'happy'
    pet.save()
    return redirect('pet_info', pet_id=pet.id)

# Сон
def put_to_sleep(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    pet.energy = 100 
    pet.mood = 'sleepy'
    pet.save()
    return redirect('pet_info', pet_id=pet.id)