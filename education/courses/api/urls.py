from django.urls import path,include
from rest_framework import routers
from . import views

app_name = 'courses'
router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet)
router.register('subjects', views.SubjectsViewSet)

urlpatterns = [
    # removed and replace by viewsets
    # path(
    #     'subjects/',
    #     views.SubjectListView.as_view(),
    #     name='subject_list'
    # ),

    # path(
    #     'subjects/<pk>/',
    #     views.SubjectDetailView.as_view(),
    #     name='subject_detail'
    # ),
    path('', include(router.urls)),




    # path(
    #     'course/',
    #     views.CourseListView.as_view(),
    #     name='course_list'
    # ),
]