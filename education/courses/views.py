from django.shortcuts import render

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from .models import Course
from django.forms import Form

from django.contrib.auth.mixins import (
    # Replicates the login_required decorator’s functionality.
    LoginRequiredMixin,
    #  Grants access to the view to users with a specific permission
    PermissionRequiredMixin
)



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
class OwnerCourseMixin(
    OwnerMixin,LoginRequiredMixin, PermissionRequiredMixin
):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    
# Enables Edit form, for Current user OwnerCourses
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'
    
# Enables List view , for Current user Courses
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'
    
# Create view for current user , current form
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'
    pass

# Update view for current user, current form
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'
    pass

# Delete view for current user, current form
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'
