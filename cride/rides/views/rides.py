"""Rides views"""

#django rest framework
from rest_framework import mixins, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

#permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember
from cride.rides.permissions.rides import IsRideOwner, IsNotRideOwner

# filters
from rest_framework.filters import SearchFilter, OrderingFilter

#serializers
from cride.rides.serializers import (
    CreateRideSerializer, 
    RideModelSerializer,
    JoinRideSerializer, 
    EndRideSerializer,
)

#models
from cride.circles.models import Circle

#utilities
from datetime import timedelta
from django.utils import timezone


class RideViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetriveModelMixin,
                  viewsets.GenericViewSet):
    """Ride view set"""

    #serializer_class = CreateRideSerializer
    #permission_classes = [IsAuthenticated, IsActiveCircleMember]

    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ('departure_date', 'arrival_date', 'available_seats')
    ordering_fileds = ('departure_date', 'arrival_date', 'available_seats')
    search_fields = ('departure_location', 'arrival_location')

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists"""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(RideViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assing permission based on action"""
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action in ['update', 'partial_update', 'finish']: #solo los dueños del ride puede editar
            permissions.append(IsRideOwner)
        if self.action == 'join':
            permissions.append(IsNotRideOwner) #este permiso es para evitar que el crea el ride se agregue
        return [p() for p in permissions]

    def get_serializer_context(self): #para agregar un contexto cuando vayya al serializer
        """Add circle to serializer context"""
        context =super(RideViewSet, self).get_serializer_context()
        context['circle'] = self.circle
        return context

    def get_serializer_class(self): #obtener el serializer de acuerdo en acciones
        """Return serializer based on action"""
        if self.action == 'create':
            return CreateRideSerializer
        if self.action == 'update':
            return JoinRideSerializer
        if self.acrion == 'finish':
            return EndRideSerializer
        return RideModelSerializer
    
    def get_queryset(self):
        """Return active circle's rides"""

        if self.action != 'finish':
            offset = timezone.now() + timedelta(minutes=10)
            return self.circle.ride_set.filter( #obtiene los rides del circulo
                departure_date__gte=offset, #sea mayor o igual a offset
                is_activate=True,
                available_seats__gte=1 #que sea mayor o igual 1
            )
        return self.circle.ride_set.all()

    @action(detail=True, methods=['post'])
    def join(self, request, *args, **kwargs):
        """Add requesting user to ride"""
        #se enviara el ride en el contexto al serializer y al pasajero como un usuario directamente
        ride = self.get_object()
        serializer_class = self.get_serializer_class() #obtiene el serializer correspondiente a la action join
        serializer = serializer_class(
            ride,
            data = {'passenger': request.user.pk},
            context= {'ride': ride, 'circle': self.circle},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finish(self, requets, *args, **kwargs):
        """Call by owners to finish a ride"""
        ride = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            ride,
            data={'is_active': False, 'current__time': timezone.now()},
            context= self.get_serializer_context(),
            partial= True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)

                

