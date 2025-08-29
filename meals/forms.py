from django import forms
from .models import MealPlanEntry, Meal
from .utils import get_default_user

class MealPlanEntryForm(forms.ModelForm):
    class Meta:
        model = MealPlanEntry
        fields = ['meal', 'day_of_week', 'meal_type', 'notes']

    def __init__(self, *args, **kwargs):
        # The user is no longer passed in, so we remove it from kwargs
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        user = get_default_user()
        if user:
            self.fields['meal'].queryset = Meal.objects.filter(created_by=user)