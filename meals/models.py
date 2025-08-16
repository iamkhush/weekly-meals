from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Meal(models.Model):
    """Model representing a basic meal."""
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_meal_type_display()})"
    
    @property
    def total_time(self):
        """Get total time from recipe if available."""
        if hasattr(self, 'recipe') and self.recipe:
            return self.recipe.prep_time + self.recipe.cook_time
        return 0
    
    @property
    def servings(self):
        """Get servings from recipe if available."""
        if hasattr(self, 'recipe') and self.recipe:
            return self.recipe.servings
        return 1


class Recipe(models.Model):
    """Model representing detailed recipe information for a meal."""
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='recipe')
    ingredients = models.TextField(help_text="List of ingredients")
    instructions = models.TextField(help_text="Cooking instructions")
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=0)
    cook_time = models.PositiveIntegerField(help_text="Cooking time in minutes", default=0)
    servings = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='easy')
    
    def __str__(self):
        return f"Recipe for {self.meal.name}"
    
    @property
    def total_time(self):
        return self.prep_time + self.cook_time


class Nutrition(models.Model):
    """Model representing nutritional information for a meal."""
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='nutrition')
    calories_per_serving = models.PositiveIntegerField(null=True, blank=True, help_text="Calories per serving")
    protein_grams = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    carbs_grams = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fat_grams = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fiber_grams = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sugar_grams = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sodium_mg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Nutrition for {self.meal.name}"


class WeeklyMealPlan(models.Model):
    """Model representing a weekly meal plan for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start_date = models.DateField()
    name = models.CharField(max_length=100, default="Weekly Meal Plan")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'week_start_date']
    
    def __str__(self):
        return f"{self.user.username}'s plan for week of {self.week_start_date}"


class MealPlanEntry(models.Model):
    """Model representing a specific meal scheduled for a specific day and meal type."""
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    meal_plan = models.ForeignKey(WeeklyMealPlan, on_delete=models.CASCADE, related_name='entries')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    meal_type = models.CharField(max_length=20, choices=Meal.MEAL_TYPES)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['meal_plan', 'day_of_week', 'meal_type']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.get_meal_type_display()}: {self.meal.name}"
