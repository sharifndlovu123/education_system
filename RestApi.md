## Extending serializers

you may want to enrich the response with additional relevant data or calculated fields. Let’s take a look at some of the options to extend serializers.

## Adding additional fields to serializers

add annotates

from django.db.models import Count
class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.annotate(total_courses=Count('courses'))
    serializer_class = SubjectSerializer
class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.annotate(total_courses=Count('courses'))
    serializer_class = SubjectSerializer




## Implementing serializer method fields
DRF provides SerializerMethodField, which allows you to implement read-only fields that get their value by calling a method of the serializer class

 useful when you want to include some custom formatted data in your serialized object or perform complex calculations that are not directly a part of your model instances.

 method that serializes the top 3 popular courses for a subject.
 ank courses by the number of students enrolled in them

 ## Adding pagination to views
 DRF includes built-in pagination capabilities to control how many objects are sent over in your API responses

 Create a new file inside the courses/api/ directory and name it pagination.py. Add the following code to it:
```python
from rest_framework.pagination import PageNumberPagination
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
```


Add the following onto our SubjectListView view
```python
from courses.api.pagination import StandardPagination
pagination_class = StandardPagination
```

Test with ?page_size=2&page=1

The json returned will no add the following extras
```markup
count: The total number of results.
next: The URL to retrieve the next page. The value is null when there are no following pages.
previous: The URL to retrieve the previous page. The value is null when there are no previous pages.
results: A list with the serialized objects returned on this page.
```




add the course Serialzier, and test it via shell

```python
# ...
from courses.models import Course, Subject
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'subject',
            'title',
            'slug',
            'overview',
            'created',
            'owner',
            'modules'
        ]

```

```markup
python manage.py shell
from rest_framework.renderers import JSONRenderer
from courses.models import Course
from courses.api.serializers import CourseSerializer
course = Course.objects.latest('id')
serializer = CourseSerializer(course)
JSONRenderer().render(serializer.data)

"modules": [6, 7, 9, 10]

```

result will print out primary key values 
So this is the nex topic,
## Serializing relations (Related Objects)
 https://www.django-rest-framework.org/api-guide/relations/.

DRF comes with different types of related fields to represent model relationships. This works for ForeignKey, ManyToManyField, and OneToOneField relationships, as well as generic model relations.

use StringRelatedField to change how related Module objects are serialized. StringRelatedField represents the related object using its __str__() method.

```python
# ...
class CourseSerializer(serializers.ModelSerializer):
    modules = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        # ...
```
 you define the modules field that provides serialization for the related Module objects. 
 
 You use many=True to indicate that you are serializing multiple related objects. The read_only parameter indicates that this field is read-only and should not be included in any input to create or update objects.


 Previous result = "modules":[44,45,46]'
 New Result = "modules":["1. Birth of Music","2. Music in production","3. Music in theatre"]

 "Note that DRF does not optimize QuerySets. When serializing a list of courses, a SQL query will be generated for each course result to retrieve the related Module objects. You can reduce the number of additional SQL requests by using prefetch_related() in your QuerySet, like Course.objects.prefetch_related('modules'). We will cover this later in the section Creating ViewSets and routers".


## Creating nested serializers
we want to include more information about each module, we need to serialize Module objects and nest them.

Modify the previous code of the api/serializers.py file of the courses

```python
from django.db.models import Count
from rest_framework import serializers
from courses.models import Course, Module, Subject
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']
class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        # ...

```

you define ModuleSerializer to provide serialization for the Module model. Then, you modify the modules attribute of CourseSerializer to nest the ModuleSerializer serializer. 
You keep many=True to indicate that you are serializing multiple objects and read_only=True to keep this field read-only.



## Creating ViewSets and routers
viewsets allow you to Define the interactions of your API and let DRF build URLs dynamically with a Router object.
By using ViewSets, you can avoid repeating logic for multiple views. ViewSets include actions for the following standard operations:

```markup
Create operation: create()
Retrieve operation: list() and retrieve()
Update operation: update() and partial_update()
Delete operation: destroy()
```


 api/views.py
```python
from django.db.models import Count
from rest_framework import generics
from rest_framework import viewsets
from courses.api.pagination import StandardPagination
from courses.api.serializers import CourseSerializer, SubjectSerializer
from courses.models import Course, Subject
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.prefetch_related('modules')
    serializer_class = CourseSerializer
    pagination_class = StandardPagination

```

CourseViewSet class inherits from ReadOnlyModelViewSet, which provides the read-only actions list() and retrieve() to list objects or retrieve a single object, respectively. 

You specify the base QuerySet to retrieve objects. You use prefetch_related('modules') to fetch the related Module objects in an efficient manner. 

This will avoid additional SQL queries when serializing nested modules for each course. In this class, you also define the serializer and pagination classes to use for the ViewSet.


add the folllowing under urls.py
```python
from django.urls import include, path
from rest_framework import routers
from . import views
app_name = 'courses'
router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet)
urlpatterns = [
    # ...
    path('', include(router.urls)),
]

```
You create a DefaultRouter object and register CourseViewSet with the courses prefix. The router takes charge of generating URLs automatically for your ViewSet.

view courses now
http://127.0.0.1:8000/api/courses/


add the same for the subjects and now go to the main api
http://127.0.0.1:8000/api

we should be able to redirect to others easier

You can learn more about ViewSets at https://www.django-rest-framework.org/api-guide/viewsets/. You can also find more information about routers at https://www.django-rest-framework.org/api-guide/routers/.


Building custom API views
implement your own views with custom logic. Let’s learn how to create a custom API view.