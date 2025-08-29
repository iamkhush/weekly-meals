from django.contrib.auth.models import User

def get_default_user():
    """Get the default user for the application."""
    try:
        return User.objects.get(username='admin')
    except User.DoesNotExist:
        return User.objects.filter(is_superuser=True).first() or User.objects.first()
