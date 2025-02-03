from rest_framework.permissions import BasePermission
class IsEnrolled(BasePermission):
    # we override the existing has_object_permission method to check if the user is enrolled in the course.
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()

