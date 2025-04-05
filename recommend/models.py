from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Course(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    duration = models.IntegerField()  # in hours
    difficulty = models.IntegerField()  # 1 = easy, 2 = medium, 3 = hard
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to="badges/", null=True, blank=True)

    def get_icon_url(self):
        if self.icon and hasattr(self.icon, 'url'):
            return self.icon.url
        return "/static/images/default_badge.jpg"  # Fallback image

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict)
    available_time = models.IntegerField(default=10)  # max hours per week
    max_courses = models.IntegerField(default=3)
    selected_courses = models.ManyToManyField(Course, blank=True, related_name="selected_by_users")
    recommended_courses = models.ManyToManyField(Course, blank=True, related_name="recommended_to_users")
    completed_courses = models.ManyToManyField(Course, blank=True, related_name="completed_by_users")
    badges = models.ManyToManyField(Badge, blank=True)
    points = models.IntegerField(default=0)
    dark_mode = models.BooleanField(default=False)
    notification_enabled = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)

    def check_badges(self):
        completed_count = self.completed_courses.count()
        badges_awarded = False
        
        # First Course Badge
        if completed_count >= 1:
            badge, created = Badge.objects.get_or_create(
                name="First Course",
                defaults={
                    "description": "Completed your first course!",
                    "icon": "badges/first_course.png"
                }
            )
            if badge not in self.badges.all():
                self.badges.add(badge)
                badges_awarded = True

        # Learning Streak Badge
        if completed_count >= 2:
            badge, created = Badge.objects.get_or_create(
                name="Learning Streak",
                defaults={
                    "description": "Completed 2 courses!",
                    "icon": "badges/learning_streak.png"
                }
            )
            if badge not in self.badges.all():
                self.badges.add(badge)
                badges_awarded = True

        return badges_awarded

    def award_points(self, points):
        """Award points to user and check for badge eligibility"""
        self.points += points
        self.save()
        return self.check_badges()

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    instance.userprofile.save()