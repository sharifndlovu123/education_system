from rest_framework import serializers
from courses.models import Subject

# The Meta class allows you to specify the model to serialize and the fields to be included for serialization. All model fields will be included if you don’t set a fields attribute. 

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']
