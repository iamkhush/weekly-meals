from django.contrib import admin
from .models import Meal, Recipe, Nutrition, WeeklyMealPlan, MealPlanEntry


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
    list_display = ['name', 'meal_type', 'get_total_time', 'get_servings', 'created_by', 'created_at']
    list_filter = ['meal_type', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RecipeInline, NutritionInline]
    
    def get_total_time(self, obj):
        return f"{obj.total_time} min" if obj.total_time > 0 else "No recipe"
    get_total_time.short_description = 'Total Time'
    
    def get_servings(self, obj):
        return obj.servings
    get_servings.short_description = 'Servings'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by when creating a new meal
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


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
    extra = 0
    autocomplete_fields = ['meal']


@admin.register(WeeklyMealPlan)
class WeeklyMealPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'week_start_date', 'created_at']
    list_filter = ['user', 'week_start_date', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MealPlanEntryInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set user when creating a new meal plan
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(MealPlanEntry)
class MealPlanEntryAdmin(admin.ModelAdmin):
    list_display = ['meal_plan', 'day_of_week', 'meal_type', 'meal', 'notes']
    list_filter = ['day_of_week', 'meal_type', 'meal_plan__user']
    search_fields = ['meal__name', 'meal_plan__name', 'notes']
    autocomplete_fields = ['meal', 'meal_plan']
