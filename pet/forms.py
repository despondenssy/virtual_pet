from django import forms
from .models import Pet

class PetForm(forms.ModelForm):
    image = forms.ChoiceField(
        choices=[
            ('pet_images/cat1.png', 'Cat 1'),
            ('pet_images/cat2.jpg', 'Cat 2'),
        ],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Pet
        fields = ['name', 'image']

class RenamePetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }