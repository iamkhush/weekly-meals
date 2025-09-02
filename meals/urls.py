from django.urls import path
from . import views

app_name = 'meals'

urlpatterns = [
    path('', views.home, name='home'),
    path('meals/', views.meal_list, name='meal_list'),
    path('meals/<int:meal_id>/', views.meal_detail, name='meal_detail'),
    path('weekly-plan/', views.weekly_meal_plan, name='weekly_meal_plan'),
    path('weekly-plan/<int:year>/<int:week>/', views.weekly_meal_plan, name='weekly_meal_plan_date'),
    path('plan-with-ai/', views.plan_with_ai, name='plan_with_ai'),
    path('update-meal-entry/', views.update_meal_plan_entry, name='update_meal_plan_entry'),
]
