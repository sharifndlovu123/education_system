from rest_framework import serializers
from courses.models import Subject, Course, Module
from django.db.models import Count
# The Meta class allows you to specify the model to serialize and the fields to be included for serialization. All model fields will be included if you don’t set a fields attribute. 

class SubjectSerializer(serializers.ModelSerializer):
    total_courses = serializers.IntegerField()

    # method name is not required, defaults to get_<field_name>
    # note to sefl: self is the instance of the serializer, obj is the instance of the model
    popular_courses = serializers.SerializerMethodField(method_name='get_popular_courses')
    def get_popular_courses(self, obj):
        courses = obj.courses.annotate(total_students=Count('students')
                                       ).order_by('-total_students')[:3]
        
        # this is a list comprehension that returns a list of strings with the course title and the total number of students enrolled in the course.
        return [
            f'{c.title} ({c.total_students})' for c in courses
        ]

    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug', 'total_courses', 'popular_courses']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    # modules = serializers.StringRelatedField(many=True, read_only=True)
    # owner = serializers.StringRelatedField()
    # subject = serializers.StringRelatedField()

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
