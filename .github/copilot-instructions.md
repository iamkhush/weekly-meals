<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Weekly Meals Django Project Instructions

## Project Overview
This is a Django application for weekly meal planning with the following key features:
- Flexible meal creation with optional recipe and nutrition details
- Weekly meal planning with day/meal type organization
- User-specific meal management
- Admin interface for data management

## Model Structure
- **Meal**: Basic meal information (name, description, meal_type, created_by)
- **Recipe**: Optional detailed recipe information (ingredients, instructions, times, difficulty)
- **Nutrition**: Optional nutritional information (calories, macros, etc.)
- **WeeklyMealPlan**: User's meal plan for a specific week
- **MealPlanEntry**: Individual meal assignments to specific days/meal types

## Development Guidelines
- Models use OneToOne relationships for Recipe and Nutrition to keep them optional
- Views should handle cases where Recipe or Nutrition data might not exist
- Use Django admin for data management with inline editing
- Templates should gracefully handle missing recipe/nutrition data
- All time-based queries should use timezone.now() for consistency

## Code Style
- Follow Django best practices
- Use descriptive model and field names
- Include helpful help_text for form fields
- Use proper null=True, blank=True for optional fields
- Keep views simple and focused on single responsibilities
