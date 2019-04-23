"""Circle Views"""

#Django REST FRamework
from rest_framework import viewsets, mixins
#permission
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.circles import IsCircleAdmin

#models 
from cride.circles.models import Circle, Membership


#Serializer
from cride.circles.serializers import CircleModelSerializer

class CircleViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """Circle view set"""
    
    serializer_class = CircleModelSerializer
    #permission_classes = (IsAuthenticated,)
    def get_permissions(self):
        """Assing circle admin"""
        permissions = [IsAuthenticated]
        if self.action in ['update', 'partial_update']:
            permissions.append(IsCircleAdmin)
        return [permission() for permission in permissions]


    def get_queryset(self):
        """Restrict list to public-only"""
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.filter(is_public=True)
        return queryset
    
    def perform_create(self, serializer):
        """Assign circle admin"""
        circle = serializer.save()
        user = self.request.user
        profile = user.profile
        Membership.objects.create(
            user = user,
            profile=profile,
            circle = circle,
            is_admin = True,
            remaining_invitations = 15
        )
    
