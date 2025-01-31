from django.forms.models import inlineformset_factory
from .models import Course, Module

# build a model formset dynamically for the Module objects related to a Course object.
ModuleFormSet = inlineformset_factory(
    Course,
    Module,
    fields=['title', 'description'],
    extra=2,
    can_delete=True
)
