from django import template

register = template.Library()

@register.filter
def get_model_name(value):
    return value._meta.model_name