from django import forms
from courses.models import Course

class CourseEnrollForm(forms.Form):
    #  use of none returns an empty query set, doesnt return any objects and doesnt query the db
    #  only query the db as needed
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.HiddenInput
    )
    
    # we query here to get the course objects
    def __init__ (self, *args, **kwargs):
        super(CourseEnrollForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()

