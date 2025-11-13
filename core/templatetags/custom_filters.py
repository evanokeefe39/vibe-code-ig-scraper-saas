import json
from django import template

register = template.Library()

@register.simple_tag
def get_dict_value(dictionary, key):
    """Get a value from a dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def parse_json(json_string):
    """Parse JSON string to dictionary"""
    if isinstance(json_string, str):
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return {}
    elif isinstance(json_string, dict):
        return json_string
    return {}