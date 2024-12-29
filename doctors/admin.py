from django.contrib import admin

from .models import Doctor, DoctorQuery


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    pass

@admin.register(DoctorQuery)
class DoctorQueryAdmin(admin.ModelAdmin):
    pass