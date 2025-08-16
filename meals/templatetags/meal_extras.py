from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup dictionary values by key."""
    if isinstance(dictionary, dict) and key in dictionary:
        return dictionary[key]
    return None
