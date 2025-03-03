from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    duration = models.IntegerField()  # in hours
    difficulty = models.IntegerField()  # 1 = easy, 2 = medium, 3 = hard

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict)
    available_time = models.IntegerField(default=10)  # max hours per week
    max_courses = models.IntegerField(default=3)

    def __str__(self):
        return self.user.username
