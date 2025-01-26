from django.shortcuts import render

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from .models import Course
from django.forms import Form


class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


# This is what helps make it only a specific user   
class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
    
# sets the owner of the created/updated object to the current user.
class OwnerEditMixin:   
    
    # override of default djangoMixin
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
# combines OwnerMixin (current user) and sets up common properties for course-related views:  shows current user courses
class OwnerCourseMixin(OwnerMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    
# Enables Edit form, for Current user OwnerCourses
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'
    
# Enables List view , for Current user Courses
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    
# Create view for current user , current form
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    pass

# Update view for current user, current form
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    pass

# Delete view for current user, current form
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
