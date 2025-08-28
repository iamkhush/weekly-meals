# Weekly Meals Planner

A Django web application for planning and managing weekly meals with optional recipe details and nutrition information.

## Features

- **Flexible Meal Management**: Create basic meals with optional detailed recipes and nutrition info
- **Weekly Planning**: Plan meals for each day of the week organized by meal type
- **Recipe Details**: Store ingredients, instructions, prep/cook times, and difficulty levels
- **Nutrition Tracking**: Optional nutritional information per meal
- **User Management**: Each user has their own meals and meal plans
- **Admin Interface**: Full Django admin interface for easy data management

## Model Structure

### Core Models
- **Meal**: Basic meal information (name, description, meal type)
- **Recipe**: Optional detailed recipe information (OneToOne with Meal)
- **Nutrition**: Optional nutritional information (OneToOne with Meal)

### Planning Models
- **WeeklyMealPlan**: User's meal plan for a specific week
- **MealPlanEntry**: Links meals to specific days and meal types

## Setup and Installation

### Prerequisites
- Python 3.8+
- Django 4.2+

### Installation Steps

1. **Clone and navigate to the project**:
   ```bash
   cd /path/to/weekly-meals
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Main app: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## Usage

### Creating Meals
1. Go to the Admin interface
2. Add a new Meal with basic information
3. Optionally add Recipe details (ingredients, instructions, times)
4. Optionally add Nutrition information

### Planning Your Week
1. Create meals first
2. Go to Admin → Meal plan entries
3. Create entries linking meals to specific days and meal types
4. View your weekly plan at `/weekly-plan/`

### Viewing Your Plans
- **Home Page**: Shows current week's plan and today's meals
- **My Meals**: Browse all your created meals
- **Weekly Plan**: Full grid view of the current week's meal plan

## Development

### Project Structure
```
weekly_meals/
├── manage.py
├── weekly_meals/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── meals/                 # Main app
    ├── models.py         # Data models
    ├── views.py          # View logic
    ├── admin.py          # Admin configuration
    ├── urls.py           # URL patterns
    ├── templates/        # HTML templates
    └── templatetags/     # Custom template filters
```

### Key Features
- **Modular Design**: Recipe and nutrition info are optional and stored separately
- **User Isolation**: Each user only sees their own meals and plans
- **Flexible Planning**: Support for all meal types and days of the week
- **Admin Integration**: Rich admin interface with inline editing

## Contributing

1. Make changes to the models, views, or templates
2. Run migrations if you changed models: `python manage.py makemigrations && python manage.py migrate`
3. Test your changes with the development server
4. Update this README if you add new features

# Deployment

## Automated Setup Using Ansible ( on Ubuntu machine )
```bash
sudo apt install ansible

git clone <your-repo-url>

# Run the playbook
ansible-playbook devops/ansible-playbook.yml --ask-become-pass

# You'll need to provide database password as extra vars:
ansible-playbook devops/ansible-playbook.yml --ask-become-pass -e "db_password=your_secure_password"
```

## License

This project is open source and available under the MIT License.
