from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Doctor(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.CharField(max_length=200)
    avatar = models.ImageField(blank=True, null=True, upload_to='images/doctor_avatar/', default='/images/no-img.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('doctor-detail', kwargs={'pk': self.pk})
    
class DoctorQuery(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.doctor.name} ask for {self.query}'