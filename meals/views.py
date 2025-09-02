from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from .forms import MealPlanEntryForm
from .models import Meal, WeeklyMealPlan, MealPlanEntry
from .utils import get_default_user
import google.generativeai as genai
from django.conf import settings

from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

def home(request):
    """Home page view with current week's meal plan preview."""
    user = get_default_user()
    context = {'user': user}
    
    if user:
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        meal_plan, created = WeeklyMealPlan.objects.get_or_create(
            user=user,
            name=f'Week of {week_start}',
            week_number=today.isocalendar()[1],
            year=today.year
        )
        
        today_entries = MealPlanEntry.objects.filter(
            meal_plan=meal_plan,
            day_of_week=today.weekday()
        ).select_related('meal')
        
        week_entries = MealPlanEntry.objects.filter(
            meal_plan=meal_plan
        ).select_related('meal')
        
        context.update({
            'meal_plan': meal_plan,
            'today_entries': today_entries,
            'week_entries_count': week_entries.count(),
            'week_start': week_start,
            'week_end': week_end,
            'today': today,
        })
    
    return render(request, 'meals/home.html', context)

def meal_list(request):
    """Display all meals."""
    user = get_default_user()
    meals = Meal.objects.filter(created_by=user).order_by('-created_at')
    return render(request, 'meals/meal_list.html', {'meals': meals})

def meal_detail(request, meal_id):
    """Display details of a specific meal."""
    user = get_default_user()
    meal = get_object_or_404(Meal, id=meal_id, created_by=user)
    return render(request, 'meals/meal_detail.html', {'meal': meal})

def weekly_meal_plan(request, year=None, week=None):
    """Display or create the current week's meal plan."""
    user = get_default_user()
    
    if year and week:
        try:
            week_start = datetime.strptime(f'{year}-{week}-1', '%G-%V-%u').date()
        except ValueError:
            return redirect('meals:weekly_meal_plan')
    else:
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        year = today.isocalendar()[0]
        week = today.isocalendar()[1]

    meal_plan, created = WeeklyMealPlan.objects.get_or_create(
        user=user,
        year=year,
        week_number=week,
        defaults={'name': f'Week of {week_start}'}
    )
    
    if request.method == 'POST':
        form = MealPlanEntryForm(request.POST, user=user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.meal_plan = meal_plan
            entry.save()
            messages.success(request, 'Meal added to your plan!')
            return redirect('meals:weekly_meal_plan_date', year=year, week=week)
    else:
        form = MealPlanEntryForm(user=user)

    entries = MealPlanEntry.objects.filter(meal_plan=meal_plan).select_related('meal')
    
    meal_grid = {}
    for day in range(7):
        meal_grid[day] = {}
        for meal_type, _ in MealPlanEntry.MEAL_TYPE_CHOICES:
            meal_grid[day][meal_type] = None
    
    for entry in entries:
        meal_grid[entry.day_of_week][entry.meal_type] = entry
    
    previous_week_date = week_start - timedelta(days=7)
    next_week_date = week_start + timedelta(days=7)
    
    previous_week_year = previous_week_date.isocalendar()[0]
    previous_week_number = previous_week_date.isocalendar()[1]
    
    next_week_year = next_week_date.isocalendar()[0]
    next_week_number = next_week_date.isocalendar()[1]

    context = {
        'meal_plan': meal_plan,
        'meal_grid': meal_grid,
        'days_of_week': MealPlanEntry.DAYS_OF_WEEK,
        'meal_types': MealPlanEntry.MEAL_TYPE_CHOICES,
        'week_start': week_start,
        'form': form,
        'previous_week_year': previous_week_year,
        'previous_week_number': previous_week_number,
        'next_week_year': next_week_year,
        'next_week_number': next_week_number,
        'is_current_week': (year == timezone.now().date().year and week == timezone.now().date().isocalendar()[1])
    }
    
    return render(request, 'meals/weekly_meal_plan.html', context)

@traceable
def plan_with_ai(request):
    context = {}
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        
        run_tree = get_current_run_tree()
        if run_tree:
            run_tree.add_inputs({'prompt': prompt})

        # Fetch past 4 weeks of meal data
        today = timezone.now().date()
        four_weeks_ago = today - timedelta(weeks=4)

        user = get_default_user()
        
        meal_entries = MealPlanEntry.objects.filter(
            meal_plan__user=user,
            meal_plan__created_at__gte=four_weeks_ago
        ).select_related('meal').order_by('meal_plan__created_at', 'day_of_week', 'meal_type')
        
        past_meals_str = ""
        for entry in meal_entries:
            past_meals_str += f"- {entry.meal_plan.name}, {entry.get_day_of_week_display()}, {entry.get_meal_type_display()}: {entry.meal.name}\n"
            
        if not past_meals_str:
            past_meals_str = "No recent meal data found."
            
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            full_prompt = f"""
            Here is my meal planning history for the last 4 weeks:
            {past_meals_str}

            Here is my request for next week's meal plan:
            "{prompt}"

            Based on my history and my request, please generate a 7-day meal plan for next week (Monday to Sunday) with Breakfast, Lunch, and Dinner.
            Please provide the output in a clear, easy-to-read format.
            """
            
            response = model.generate_content(full_prompt)
            context['suggestion'] = response.text

            if run_tree:
                run_tree.add_outputs({'suggestion': response.text})

            # Update current trace with token usage
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                if run_tree:
                    usage_data = {
                        'prompt_tokens': response.usage_metadata.prompt_token_count,
                        'completion_tokens': response.usage_metadata.candidates_token_count,
                        'total_tokens': response.usage_metadata.total_token_count
                    }
                    run_tree.update(usage=usage_data)

        except Exception as e:
            context['error'] = f"An error occurred while generating the meal plan: {e}"

    return render(request, 'meals/plan_with_ai.html', context)
