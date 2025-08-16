from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Meal, WeeklyMealPlan, MealPlanEntry


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Meal, WeeklyMealPlan, MealPlanEntry


def home(request):
    """Home page view with current week's meal plan preview."""
    context = {'user': request.user}
    
    if request.user.is_authenticated:
        # Get the start of the current week (Monday)
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        try:
            meal_plan = WeeklyMealPlan.objects.get(
                user=request.user,
                week_start_date=week_start
            )
            
            # Get today's meals
            today_entries = MealPlanEntry.objects.filter(
                meal_plan=meal_plan,
                day_of_week=today.weekday()
            ).select_related('meal')
            
            # Get this week's meal count
            week_entries = MealPlanEntry.objects.filter(
                meal_plan=meal_plan
            ).select_related('meal')
            
            context.update({
                'meal_plan': meal_plan,
                'today_entries': today_entries,
                'week_entries_count': week_entries.count(),
                'week_start': week_start,
                'today': today,
            })
            
        except WeeklyMealPlan.DoesNotExist:
            context['no_meal_plan'] = True
    
    return render(request, 'meals/home.html', context)


@login_required
def meal_list(request):
    """Display all meals created by the user."""
    meals = Meal.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'meals/meal_list.html', {'meals': meals})


@login_required
def meal_detail(request, meal_id):
    """Display details of a specific meal."""
    meal = get_object_or_404(Meal, id=meal_id, created_by=request.user)
    return render(request, 'meals/meal_detail.html', {'meal': meal})


@login_required
def weekly_meal_plan(request):
    """Display or create the current week's meal plan."""
    # Get the start of the current week (Monday)
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    meal_plan, created = WeeklyMealPlan.objects.get_or_create(
        user=request.user,
        week_start_date=week_start,
        defaults={'name': f'Week of {week_start}'}
    )
    
    # Get all entries for this meal plan organized by day and meal type
    entries = MealPlanEntry.objects.filter(meal_plan=meal_plan).select_related('meal')
    
    # Organize entries in a grid structure for the template
    meal_grid = {}
    for day in range(7):  # Monday(0) to Sunday(6)
        meal_grid[day] = {}
        for meal_type, _ in Meal.MEAL_TYPES:
            meal_grid[day][meal_type] = None
    
    for entry in entries:
        meal_grid[entry.day_of_week][entry.meal_type] = entry
    
    context = {
        'meal_plan': meal_plan,
        'meal_grid': meal_grid,
        'days_of_week': MealPlanEntry.DAYS_OF_WEEK,
        'meal_types': Meal.MEAL_TYPES,
        'week_start': week_start,
    }
    
    return render(request, 'meals/weekly_meal_plan.html', context)
