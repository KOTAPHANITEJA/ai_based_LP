import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from scipy.optimize import linprog
from .models import Course, UserProfile
from .forms import UserRegistrationForm, UserProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .forms import CourseForm

def recommend_courses(user_profile):
    preferences = user_profile.preferences
    max_time = user_profile.available_time
    max_courses = user_profile.max_courses

    courses = Course.objects.all()
    n = len(courses)

    if n == 0:
        return []

    c = [-preferences.get(course.category, 1) for course in courses]
    A = [[course.duration for course in courses], [course.difficulty for course in courses], [1] * n]
    b = [max_time, 3, max_courses]
    result = linprog(c, A_ub=A, b_ub=b, method="highs")
    return [courses[i] for i in range(n) if result.x[i] > 0.5]

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    recommended_courses = recommend_courses(user_profile)
    all_courses = Course.objects.all()  # Fetch all courses
    
    return render(request, "dashboard.html", {
        "recommended_courses": recommended_courses,
        "all_courses": all_courses  # Pass all courses to the template
    })

def add_to_recommended(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    
    # AI-based suggestion logic
    if course.duration > user_profile.available_time:
        messages.warning(request, f"{course.title} might be too time-consuming for you. Consider a shorter course.")
    elif course.difficulty > 3:  # Assuming 3 is the average difficulty
        messages.warning(request, f"{course.title} is too difficult. Try an easier course.")
    else:
        preferences = user_profile.preferences
        preferences[course.category] = preferences.get(course.category, 1) + 1
        user_profile.preferences = preferences
        user_profile.save()
        messages.success(request, f"{course.title} added successfully!")
    
    return redirect("dashboard")

def remove_from_recommended(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    
    # Remove course category from user preferences if it exists
    preferences = user_profile.preferences
    if course.category in preferences and preferences[course.category] > 0:
        preferences[course.category] -= 1
        if preferences[course.category] == 0:
            del preferences[course.category]
    user_profile.preferences = preferences
    user_profile.save()
    messages.info(request, f"{course.title} has been removed from recommended courses.")
    
    return redirect("dashboard")

def home(request):
    return render(request, "home.html")

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"form": form})

@login_required
def profile_settings(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, "profile.html", {"form": form})

def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")  # Redirect to the dashboard after adding a course
    else:
        form = CourseForm()
    return render(request, "add_course.html", {"form": form})