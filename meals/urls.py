from django.urls import path
from . import views

app_name = 'meals'

urlpatterns = [
    path('', views.home, name='home'),
    path('meals/', views.meal_list, name='meal_list'),
    path('meals/<int:meal_id>/', views.meal_detail, name='meal_detail'),
    path('weekly-plan/', views.weekly_meal_plan, name='weekly_meal_plan'),
]
