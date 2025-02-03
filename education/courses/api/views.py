from rest_framework import generics, viewsets
from courses.api.serializers import SubjectSerializer, CourseSerializer
from courses.models import Subject, Course
from django.db.models import Count
from courses.api.pagination import StandardPagination 

# CRUD implementation is done with the ModelViewSet class

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


from rest_framework.decorators import action
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from courses.api.permissions import IsEnrolled
from courses.api.serializers import CourseWithContentsSerializer

# added extra actions to viewsets
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.prefetch_related('modules')
    serializer_class = CourseSerializer
    pagination_class = StandardPagination

    @action(
        # if its on a detail page so single object, method is a POST, and the user is authenticated, the enroll method will be called.
        detail=True,
        methods=['post'],
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated]
    )
    def enroll(self, request, *args, **kwargs):
        # self.get_object() to retrieve the Course object.
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})
    

    # only users enrolled in the course are able to access its contents.
    @action(
        detail=True,
        methods=['get'],
        serializer_class=CourseWithContentsSerializer,
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated, IsEnrolled]
    )
    def contents(self, request, *args, **kwargs):
        # helps return the Course object
        return self.retrieve(request, *args, **kwargs)
    
# class CourseListView(generics.ListAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     pagination_class = StandardPagination


# view for users to enroll in courses
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

# this is a custom view that subclasses APIView
# not in use anymore, replaced by actions in viewsets
class CourseEnrollView(APIView):
    # only identifies user (anonymous or known user)
    authentication_classes = [BasicAuthentication]
    # only authenticated users will be allowed to access
    permission_classes = [IsAuthenticated]
    #  no other HTTP method will be allowed for this view.
    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return Response({'enrolled': True})