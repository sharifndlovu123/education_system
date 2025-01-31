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


#  show list  of courses for specifc user, we override the default get query set to ensure, it returns current user courses
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

# Update view for current user, current form
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

# Delete view for current user, current form
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'





from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

# handles the formset to add, update, and delete modules for a specific course.
# MIXIN, endering templates and returning an HTTP response. 
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None
    
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)
    
    #  delegates http request to either get or post, this is an override.
    def dispatch(self, request, pk):
        self.course = get_object_or_404(
            Course, id=pk, owner=request.user
        )
        return super().dispatch(request, pk)
    
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        #  render_to_response() comes from the mixin.
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )
        
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )



# dispatch mehtod explain . 
# dispatch(): This method is provided by the View class. It takes an HTTP request and its parameters and attempts to delegate to a lowercase method that matches the HTTP method used.
# A GET request is delegated to the get() method and a POST request to post(), respectively. 
# In this method, you use the get_object_or_404() shortcut function to get the Course object for the given id parameter that belongs to the current user. 
# You include this code in the dispatch() method because you need to retrieve the course for both GET and POST requests. 
# You save it into the course attribute of the view to make it accessible to other methods.


from django.apps import apps
from django.forms.models import modelform_factory
from .models import Module, Content

#  we have 4 different types of content, meaning we might have to create 4 different views and 4 different forms. 

# View Class
# Django's View class provides a base for handling HTTP requests (GET, POST, etc.).
# You define methods like get(), post(), etc., inside the class.
class ContentCreateUpdateView(TemplateResponseMixin, View):
    # create and update different models’ contents 
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    
    def get_model(self, model_name):
        # help build the form dynamically
        if model_name in ['text', 'video', 'image', 'file']:
            # obtain the actual class for the given model name. 
            return apps.get_model(
                app_label='courses', model_name=model_name
            )
        return None
    def get_form(self, model, *args, **kwargs):
        #  modelform_facotry builds the form 
        #  use the exclude parameter to specify the common fields to exclude from the form and let all other attributes be included automatically. 
        # By doing so, you don’t have to know which fields to include depending on the model.
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated']
        )
        return Form(*args, **kwargs)
    
    # model name: The model name of the content to create/update.
    # model id: The ID for the module that the content is/will be associated with.
    # id: The ID of the object that is being updated. It’s None to create new objects.
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        self.model = self.get_model(model_name)
        #  this is what give the id
        if id:
            self.obj = get_object_or_404(
                self.model, id=id, owner=request.user
            )
        return super().dispatch(request, module_id, model_name, id)
    

    def get(self, request, module_id, model_name, id=None):
        # if  dispatch, provides no id, then no obj remains on form create
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response(
            {'form': form, 'object': self.obj}
        )
        
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(
            self.model,
            instance=self.obj,
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            
            if not id:
                # create new content, relate this piece of content to specific module
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        # invalid form
        return self.render_to_response(
            {'form': form, 'object': self.obj}
        )


# get(): Executed when a GET request is received. You build the model form for the Text, Video, Image, or File instance that is being updated. Otherwise, you pass no instance to create a new object since self.obj is None if no ID is provided.

# post(): Executed when a POST request is received. You build the model form, passing any submitted data and files to it. Then, you validate it. If the form is valid, you create a new object and assign request.user as its owner before saving it to the database. You check for the id parameter. If no ID is provided, you know the user is creating a new object instead of updating an existing one. If this is a new object, you create a content object for the given module and associate the new content with it.


# delete a piece of content from module, and go back to that specific module
class ContentDeleteView(View):
    
    def post(self, request, id):
        content = get_object_or_404(
            Content, id=id, module__course__owner=request.user
        )
        
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

# view list of content
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    
    def get(self, request, module_id):
        module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        return self.render_to_response({'module': module})



from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
#  receives the new order of module IDs encoded in JSON and updates the order accordingly
class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        
        for id, order in self.request_json.items():
            # iterates through each module, and filters by id, and ensures it matches a specific user
            # once valide, change a attribute via update
            Module.objects.filter(
                id=id, course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id, module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})

# show all courses
from django.db.models import Count
from .models import Subject
class CourseListView(TemplateResponseMixin, View):
    # if a slug is provided, filter the courses by the subject with the given slug, if no slug is provided, return all courses.
    model = Course
    template_name = 'courses/course/list.html'
    
    #  annotate adds an additional field to the query set
    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(
            total_courses=Count('courses')
        )
        courses = Course.objects.annotate(
            total_modules=Count('modules')
        )
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response(
            {
                'subjects': subjects,
                'subject': subject,
                'courses': courses
            }
        )



# display single course overview, expects a pk parameter in the URL to identify the course to display.
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm
# we use the form to display the info 
class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    def get_context_data(self, **kwargs):
        print(self.object)
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course':self.object}
        )
        return context
