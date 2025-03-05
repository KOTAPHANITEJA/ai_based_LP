from django.contrib import admin
from .models import Course
from .models import UserProfile

# Register your models here.
admin.site.register(Course)
admin.site.register(UserProfile)