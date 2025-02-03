from rest_framework import generics, viewsets
from courses.api.serializers import SubjectSerializer, CourseSerializer
from courses.models import Subject, Course
from django.db.models import Count
from courses.api.pagination import StandardPagination


class SubjectsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.annotate(total_courses=Count('courses'))
    serializer_class = SubjectSerializer
    pagination_class = StandardPagination
    
# class SubjectListView(generics.ListAPIView):
#     queryset = Subject.objects.annotate(total_courses=Count('courses'))
#     serializer_class = SubjectSerializer
#     pagination_class = StandardPagination
# class SubjectDetailView(generics.RetrieveAPIView):
#     # queryset = Subject.objects.all()
#     queryset = Subject.objects.annotate(total_courses=Count('courses'))
#     serializer_class = SubjectSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.prefetch_related('modules')
    serializer_class = CourseSerializer
    pagination_class = StandardPagination
    
# class CourseListView(generics.ListAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     pagination_class = StandardPagination