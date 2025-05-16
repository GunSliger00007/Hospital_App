from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Address)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Blog_Post)
admin.site.register(Appointment)
