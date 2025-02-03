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

## Building custom API views

DRF provides an APIView class that builds API functionality on top of Django’s View class

The APIView class differs from View by using DRF’s custom Request and Response objects and handling APIException exceptions to return the appropriate HTTP responses. 
It also has a built-in authentication and authorization system to manage access to views.

create a view for users to enroll in courses. Edit the api/views.py file of the courses application and add the following code

```python
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
class CourseEnrollView(APIView):
    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return Response({'enrolled': True})
```
Steps
    1. You create a custom view that subclasses APIView.

    2. You define a post() method for POST actions. No other HTTP method will be allowed for this view.

    3. You expect a pk URL parameter containing the ID of a course. You retrieve the course by the given pk parameter and raise a 404 exception if it’s not found.

    4. You add the current user to the students many-to-many relationship of the Course object and return a successful response.

add corresponding url:
```python
path(
    'courses/<pk>/enroll/',
    views.CourseEnrollView.as_view(),
    name='course_enroll'
),
```

Theoretically, you could now perform a POST request to enroll the current user in a course. However, you need to be able to identify the user and prevent unauthenticated users from accessing this view. Let’s see how API authentication and permissions work.




## Handling Authentication
https://www.django-rest-framework.org/api-guide/authentication/.
DRF provides authentication classes to identify the user performing the request. If authentication is successful, the framework sets the authenticated User object in request.user. 

If no user is authenticated, an instance of Django’s AnonymousUser is set instead.

DRF provides the following authentication backends:
```markup

1. BasicAuthentication: This is HTTP basic authentication. The user and password are sent by the client in the Authorization HTTP header, encoded with Base64. You can learn more about it at https://en.wikipedia.org/wiki/Basic_access_authentication.

2. TokenAuthentication: This is token-based authentication. A Token model is used to store user tokens. Users include the token in the Authorization HTTP header for authentication.

3. SessionAuthentication: This uses Django’s session backend for authentication. This backend is useful for performing authenticated AJAX requests to the API from your website’s frontend.

4. RemoteUserAuthentication: This allows you to delegate authentication to your web server, which sets a REMOTE_USER environment variable.
```

You can build a custom authentication backend by subclassing the BaseAuthentication class provided by DRF and overriding the authenticate() method.

### Implementing basic authentication
You can set authentication on a 'per-view basis' or set it 'globally' with the DEFAULT_AUTHENTICATION_CLASSES setting.

NB - Authentication only identifies the user performing the request.  It won’t allow or deny access to views. You have to use permissions to restrict access to views.

add to existing courseEnroll under api/views.py 
```python
# ...
from rest_framework.authentication import BasicAuthentication
class CourseEnrollView(APIView):
    authentication_classes = [BasicAuthentication]
    # ...
```

### Adding permissions to views

DRF includes a permission system to restrict access to views. Some of the built-in permissions of DRF are:

```markup
1. AllowAny: Unrestricted access, regardless of whether a user is authenticated or not.

2. IsAuthenticated: Allows access to authenticated users only.

3. IsAuthenticatedOrReadOnly: Complete access to authenticated users. Anonymous users are only allowed to execute read methods such as GET, HEAD, or OPTIONS.

4. DjangoModelPermissions: Permissions tied to django.contrib.auth. The view requires a queryset attribute. Only authenticated users with model permissions assigned are granted permission.

5. DjangoObjectPermissions: Django permissions on a per-object basis.

Denied permissions return 
HTTP 401: Unauthorized
HTTP 403: Permission denied
```

Add the following to api/views.py 
```python

from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
class CourseEnrollView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

```