from django import forms 

from .models import Medicine, Category, Brand

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['brand', 'category', 'name', 'price', 'stock', 'description', 'image']
