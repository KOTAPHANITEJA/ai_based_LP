from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("profile/", views.profile_settings, name="profile_settings"),

    path("add_course/", views.add_course, name="add_course"),
    path("add-to-recommended/<int:course_id>/", views.add_to_recommended, name="add_to_recommended"),
    path("remove-from-recommended/<int:course_id>/", views.remove_from_recommended, name="remove_from_recommended"),  # Add this line
]