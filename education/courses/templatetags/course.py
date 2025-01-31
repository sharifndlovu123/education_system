from django import template
register = template.Library()

#  returns the object model name, (file, text, image or video). since the template doesnt allow _meta
@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None
