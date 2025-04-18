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
    path('remove_course/<int:course_id>/', views.remove_course, name='remove_course'),
    path("add-to-recommended/<int:course_id>/", views.add_to_recommended, name="add_to_recommended"),
    path("remove-from-recommended/<int:course_id>/", views.remove_from_recommended, name="remove_from_recommended"),  # Add this line
    path("add_to_selected/<int:course_id>/", views.add_to_selected, name="add_to_selected"),
    path("remove_from_selected/<int:course_id>/", views.remove_from_selected, name="remove_from_selected"),
    path("mark_as_completed/<int:course_id>/", views.mark_as_completed, name="mark_as_completed"),
    path("remove_from_completed/<int:course_id>/", views.remove_from_completed, name="remove_from_completed"),
    path("check-badges/", views.check_badges, name="check_badges"),
    path('engineering-courses/', views.engineering_courses, name='engineering_courses'),

]