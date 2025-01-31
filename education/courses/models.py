from django.contrib.auth.models import User
from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .fields import OrderField

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        ordering = ['title']
    def __str__(self):
        return self.title
    
class Course(models.Model):
    owner = models.ForeignKey(
        User,
        related_name='courses_created',
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        related_name='courses',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(
        User,
        related_name='courses_joined',
        blank=True
    )

    
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return self.title
    
class Module(models.Model):
    course = models.ForeignKey(
        Course, related_name='modules', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # uses self numering to order the courses
    order = OrderField(blank=True, for_fields=['course'])
    class Meta:
        ordering = ['order']
    def __str__(self):
        return f'{self.order}. {self.title}'



# Content model that represents the modules’ contents and define a generic relation to associate any object with the content object.
class Content(models.Model):
    module = models.ForeignKey(
        Module,
        related_name='contents',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        # You use the model__in field lookup to filter the query to the ContentType objects with a model attribute that is 'text', 'video', 'image', or 'file'.
        limit_choices_to={
            'model__in':('text', 'video', 'image', 'file')
        }
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    class Meta:
        ordering = ['order']


from django.template.loader import render_to_string
#  an abstract base model that is then extended by models – each designed to store a particular type of data: text, image, video, and file.
class ItemBase(models.Model):
    owner = models.ForeignKey(User,
        related_name='%(class)s_related',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    def __str__(self):
        return self.title
    
    # rendering a template and returning the rendered content as a string. 
    # The render() method provides a common interface for rendering diverse content.
    def render(self):
        print("render success")
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item': self}
        )
        
class Text(ItemBase):
    content = models.TextField()
class File(ItemBase):
    file = models.FileField(upload_to='files')
class Image(ItemBase):
    file = models.FileField(upload_to='images')
class Video(ItemBase):
    url = models.URLField()

