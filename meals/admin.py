from django.contrib import admin
from .models import Meal, Recipe, Nutrition, WeeklyMealPlan, MealPlanEntry
from django import forms
from django.utils import timezone
from django.http import JsonResponse
from django.urls import path
from django.db.models import Q


class RecipeInline(admin.StackedInline):
    model = Recipe
    extra = 0
    fields = ['ingredients', 'instructions', 'prep_time', 'cook_time', 'servings', 'difficulty']


class NutritionInline(admin.StackedInline):
    model = Nutrition
    extra = 0
    fields = [
        'calories_per_serving', 'protein_grams', 'carbs_grams', 
        'fat_grams', 'fiber_grams', 'sugar_grams', 'sodium_mg'
    ]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'search_similar_names_button', 'meal_type', 'get_total_time', 'get_servings', 'created_by', 'created_at']
    list_filter = ['meal_type', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RecipeInline, NutritionInline]
    change_form_template = "admin/meals/meal/change_form_with_search.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('search-similar/', self.admin_site.admin_view(self.search_similar_meals), name='meals_meal_search_similar'),
        ]
        return custom_urls + urls

    def search_similar_meals(self, request):
        """AJAX endpoint to search for similar meals"""
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'meals': []})
        
        # Search for similar meals using name and description
        similar_meals = Meal.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('created_by').prefetch_related('recipe', 'nutrition')[:10]
        
        meals_data = []
        for meal in similar_meals:
            meals_data.append({
                'id': meal.id,
                'name': meal.name,
                'description': meal.description or '',
                'meal_type': meal.meal_type,
                'meal_type_display': meal.get_meal_type_display(),
                'created_by': meal.created_by.username if meal.created_by else 'Unknown',
                'has_recipe': hasattr(meal, 'recipe') and meal.recipe is not None,
                'has_nutrition': hasattr(meal, 'nutrition') and meal.nutrition is not None,
                'created_at': meal.created_at.strftime('%Y-%m-%d'),
            })
        
        return JsonResponse({'meals': meals_data})
    
    def get_total_time(self, obj):
        if hasattr(obj, 'recipe') and obj.recipe and obj.recipe.total_time:
            return f"{obj.recipe.total_time} min"
        return "No recipe"
    get_total_time.short_description = 'Total Time'

    def get_servings(self, obj):
        if hasattr(obj, 'recipe') and obj.recipe and obj.recipe.servings:
            return obj.recipe.servings
        return "-"
    get_servings.short_description = 'Servings'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['created_by'].initial = request.user
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        if not obj.pk and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def search_similar_names_button(self, obj):
        return ""
    search_similar_names_button.short_description = "Search Similar Names"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['meal', 'prep_time', 'cook_time', 'total_time', 'servings', 'difficulty']
    list_filter = ['difficulty', 'prep_time', 'cook_time']
    search_fields = ['meal__name', 'ingredients', 'instructions']
    autocomplete_fields = ['meal']


@admin.register(Nutrition)
class NutritionAdmin(admin.ModelAdmin):
    list_display = ['meal', 'calories_per_serving', 'protein_grams', 'carbs_grams', 'fat_grams']
    search_fields = ['meal__name']
    autocomplete_fields = ['meal']


class MealPlanEntryInline(admin.TabularInline):
    model = MealPlanEntry
    extra = 1
    autocomplete_fields = ['meal']
    fields = ['day_of_week', 'meal_type', 'meal', 'notes']

    def get_queryset(self, request):
        """Optimize queryset for inline display"""
        qs = super().get_queryset(request)
        return qs.select_related('meal', 'meal_plan')

@admin.register(MealPlanEntry)
class MealPlanEntryAdmin(admin.ModelAdmin):
    list_display = ['get_plan_name', 'get_day_display', 'get_meal_type_display', 'meal', 'get_meal_creator']
    list_filter = ['day_of_week', 'meal_type', 'meal_plan__user']
    search_fields = ['meal__name', 'meal_plan__name', 'notes']
    autocomplete_fields = ['meal', 'meal_plan']

    def get_plan_name(self, obj):
        return obj.meal_plan.name if obj.meal_plan else 'No Plan'
    get_plan_name.short_description = 'Weekly Plan'
    
    def get_day_display(self, obj):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week] if 0 <= obj.day_of_week <= 6 else 'Unknown'
    get_day_display.short_description = 'Day'
    
    def get_meal_type_display(self, obj):
        return obj.get_meal_type_display()
    get_meal_type_display.short_description = 'Meal Type'
    
    def get_meal_creator(self, obj):
        return obj.meal.created_by.username if obj.meal and obj.meal.created_by else 'Unknown'
    get_meal_creator.short_description = 'Meal Creator'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filter meals to show only user's meals for better UX
        if 'meal' in form.base_fields:
            form.base_fields['meal'].queryset = Meal.objects.filter(
                created_by=request.user
            ).order_by('meal_type', 'name')
        return form

class WeeklyMealPlanAdminForm(forms.ModelForm):
    class Meta:
        model = WeeklyMealPlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now()
        current_week = now.isocalendar()[1]
        current_year = now.year
        if not self.instance.pk:
            self.fields['week_number'].initial = current_week
            self.fields['year'].initial = current_year
            self.fields['name'].initial = f"Meal Plan {current_year} - Week {current_week}"

@admin.register(WeeklyMealPlan)
class WeeklyMealPlanAdmin(admin.ModelAdmin):
    form = WeeklyMealPlanAdminForm
    list_display = ['name', 'user', 'week_number', 'created_at']
    list_filter = ['user', 'week_number', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MealPlanEntryInline]

    def save_model(self, request, obj, form, change):
        if not change:  # Only set user when creating a new meal plan
            obj.user = request.user
        # Ensure name, week_number, and year are set if not provided
        if not obj.name:
            now = timezone.now()
            obj.name = f"Meal Plan {now.year} - Week {now.isocalendar()[1]}"
        if not obj.week_number:
            obj.week_number = timezone.now().isocalendar()[1]
        if not obj.year:
            obj.year = timezone.now().year
        super().save_model(request, obj, form, change)
