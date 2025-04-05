import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from scipy.optimize import linprog
from .models import Course, UserProfile
from .forms import UserRegistrationForm, UserProfileForm,UserRegistrationForm
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
    completed_count = user_profile.completed_courses.count()
    
    # Calculate badge progress
    first_course_progress = min(completed_count * 100, 100)  # 1 course needed
    learning_streak_progress = min(completed_count * 50, 100)  # 2 courses needed
    
    # Get top users for leaderboard
    top_users = UserProfile.objects.order_by('-points')[:10]
    
    context = {
        'user_profile': user_profile,
        'selected_courses': user_profile.selected_courses.all(),
        'recommended_courses': user_profile.recommended_courses.all(),
        'completed_courses': user_profile.completed_courses.all(),
        'all_courses': Course.objects.filter(is_removed=False),
        'first_course_progress': first_course_progress,
        'learning_streak_progress': learning_streak_progress,
        'top_users': top_users,
    }
    
    return render(request, "dashboard.html", context)


def add_to_selected(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    
    # Ensure course is not already in selected courses
    if course not in user_profile.selected_courses.all():
        user_profile.selected_courses.add(course)
        user_profile.save()
        messages.success(request, f"{course.title} added to Selected Courses!")
    else:
        messages.warning(request, f"{course.title} is already in Selected Courses!")
    
    return redirect("dashboard")


def add_to_recommended(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    selected_courses = user_profile.selected_courses.all()

    # AI suggests the best course based on selected ones
    best_course = recommend_best_course(selected_courses, user_profile)

    if best_course:
        user_profile.recommended_courses.add(best_course)
        user_profile.save()
        messages.success(request, f"{best_course.title} has been added to Recommended Courses based on your selection!")
    else:
        messages.warning(request, "No suitable course found for recommendation. Try adding more diverse courses.")

    return redirect("dashboard")



def remove_from_selected(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    
    if course in user_profile.selected_courses.all():
        user_profile.selected_courses.remove(course)
        user_profile.save()
        messages.info(request, f"{course.title} removed from Selected Courses.")
    
    return redirect("dashboard")


def remove_from_recommended(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = Course.objects.get(id=course_id)
    
    if course in user_profile.recommended_courses.all():
        user_profile.recommended_courses.remove(course)
        user_profile.save()
        messages.info(request, f"{course.title} removed from Recommended Courses.")
    
    return redirect("dashboard")

def recommend_best_course(selected_courses, user_profile):
    """AI-based recommendation allowing cross-category suggestions"""
    if not selected_courses:
        return None  # If no courses are selected, return None

    category_counts = {}
    for course in selected_courses:
        category_counts[course.category] = category_counts.get(course.category, 0) + 1

    # Find the most frequently chosen category
    best_category = max(category_counts, key=category_counts.get)

    # First, try recommending from the same category
    recommended_course = Course.objects.filter(
        category=best_category
    ).exclude(id__in=[course.id for course in selected_courses] + [course.id for course in user_profile.recommended_courses.all()]).first()

    # If no course found, try from any category (cross-category recommendation)
    if not recommended_course:
        recommended_course = Course.objects.exclude(
            id__in=[course.id for course in selected_courses] + [course.id for course in user_profile.recommended_courses.all()]
        ).first()

    return recommended_course  # Returns at least one course or None if no courses exist




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
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile for the new user
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

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

def remove_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.info(request, f"{course.title} has been removed from available courses.")
    return redirect("dashboard")


def mark_as_completed(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # Remove from selected or recommended if present
    if course in user_profile.selected_courses.all():
        user_profile.selected_courses.remove(course)
    if course in user_profile.recommended_courses.all():
        user_profile.recommended_courses.remove(course)
    
    # Add to completed courses
    user_profile.completed_courses.add(course)
    user_profile.save()

     # Award points based on course difficulty
    points_to_award = course.difficulty * 100  # Example: harder courses = more points
    user_profile.award_points(points_to_award)
    messages.success(request, f"Congratulations! You've completed {course.title} and earned {points_to_award} points!!")
    return redirect("dashboard")


def remove_from_completed(request, course_id):
    user_profile = UserProfile.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    
    if course in user_profile.completed_courses.all():
        user_profile.completed_courses.remove(course)
        user_profile.save()
        messages.info(request, f"{course.title} removed from Completed Courses.")
    
    return redirect("dashboard")

@login_required
def check_badges(request):
    user_profile = UserProfile.objects.get(user=request.user)
    initial_badge_count = user_profile.badges.count()
    user_profile.check_badges()
    final_badge_count = user_profile.badges.count()
    
    if final_badge_count > initial_badge_count:
        new_badge = user_profile.badges.last()
        messages.success(request, f"Congratulations! You've earned new badges! Current points: {user_profile.points}")
        return render(request, 'dashboard.html', {
            'new_badge': new_badge,
            'user_profile': user_profile
        })
    else:
        messages.info(request, f"Current points: {user_profile.points} - Complete more courses to earn badges!")
        return redirect("dashboard")
    
    
def engineering_courses(request):
    return render(request, 'engineering_courses.html')

#points system:
#Easy course (difficulty 1) = 100 points
#Medium course (difficulty 2) = 200 points
#Hard course (difficulty 3) = 300 points