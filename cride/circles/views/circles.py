"""Circle Views"""

#Django REST FRamework
from rest_framework import viewsets, mixins
#permission
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.circles import IsCircleAdmin

#Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

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
    lookup_field = 'slug_name' #define que con este campo se llamara cuando se llama en la url. para obtener la informacion detallada de un circulo
    #permission_classes = (IsAuthenticated,)

    #Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('slug_name', 'name')
    ordering_fields = ('rides_offered', 'rides_taken', 'name', 'created', 'member_limit')
    ordering  = ('-members__count', '-rides_offered', '-rides_taken') #para ordenar por defecto
    filter_fields = ('verified', 'is_limited')

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
    
