"""Rides serializers"""

#django rest frmawork
from rest_framework import serializers

#models
from cride.rides.models import Ride
from cride.circles.models import Membership
from cride.users.models import User

#serializers
from cride.users.serializers import UserModelSerializer

#utilities
from datetime import timedelta
from django.utils import timezone

class CreateRideSerializer(serializers.ModelSerializer):
    """Create ride serializers"""

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault()) #recibe lo que se manda en el contexto
    available_seats = serializers.IntegerField(min_value=1, max_value=15)

    class Meta:
        """Meta class"""
        model = Ride
        exclude = ('offered_in', 'passengers', 'rating', 'is_activate')

    #validar la fecha
    def validate_departure_date(self, data):
        """Verifay date is not in the pasts"""
        min_date = timezone.now() + timedelta(minutes=10)
        if data < min_date:
            raise serializers.ValidationError(
                'Departure time must be at least pass the next 20 minutes windows'
            )
        return data

    def validate(self, data):
        """Validate.
        Verify that the person who offers tge ride is member
        and also the same user making the request.
        """
              #contexto                     #data del hidden  #verificar que sean el mismo usuario
        if self.context['request'].user != data['offered_by']:
            raise serializers.ValidationError('Rides offred on behalf of others are not allowed')

        #verificar la membresia del usuario
        user = data['offered_by']
        circle = self.context['circle']
        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an activate member of the circle')

        #Verificar la fecha de llegada no sea menor a la fecha de salida
        if data['arrival_date'] <= data['departure_date']:
            raise serializers.ValidatationError('Departure dte must happen ofter arrival date.')
        
        #agregar membership en el contexto
        self.context['membership'] = membership
        return data

    def create(self, data):
        """Create ride and update stats"""
        circle = self.context['circle']
        ride = Ride.objects.create(**data, offered_in=circle)

        #circle
        circle.rides_offered += 1
        circle.save()

        #membership
        membership = self.context['membership']
        membership.rides_offered += 1
        membership.save()

        #profile
        profile = data['offered_by'].profile
        profile.rides_offered += 1
        profile.save()

        return ride

class RideModelSerializer(serializers.ModelSerializer):
    """Ride model serializer"""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField()

    #para que no se puedan editar los pasajeros
    passengers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        """Meta class"""
        model = Ride
        fields = '__all__'
        read_only_fields = (
           'offered_by',
           'offered_in',
           'rating'
        )
    
    #para asegurar, de que cuando un viaje este en proceso no se pueda obtener ningun dato
    #lo que se verifica es que si la fecha del rides es mayor al tiempo actual no se podran modificar datos
    def update(self, instance, data):
        """Allow updates only before departure date"""
        now = timezone.now()
        if instance. departure_date <= now:
            raise serializers.ValidationError('Ongoing rides cannot be modified')
        return super(RideModelSerializer, self).update(instance, data)

class JoinRideSerializer(serializers.ModelSerializer):
    """Join ride serializer"""

    passenger = serializers.IntegerField()

    class Meta:
        """Meta class"""
        model = Ride
        fields = ('passenger',)

    def validate_passenger(self, data):
        """Verify passenger exists and is a circle member"""
        try:
            user = User.objects.get(pk=data)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid passenger')
        
        circle = self.context['circle']

        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
        except membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle')

        self.context['user'] = user
        self.context['member'] = membership
        return data

    def validate(self, data):
        """verify rides allow new passengers"""
        #
        ride = self.context['ride'] #verifica que el ride esta en el tiempo aducado
        if ride.departure_date <= timezone.now():
            raise serializers.ValidationError("You can't join this ride now")

        if ride.available_seats < 1: #verifca que haya asientos disponibles
            raise serializers.ValidationError("Ride is already full!")

        if Ride.objects.filter(passengers__pk=data['passenger']): #verifica que el user no este en el ride
            raise serializers.ValidationError('Passenger is already in this trip')

        return data

    def update(self, instance, data):
        """Add passemger to ride, and update stats"""
        ride = self.context['ride']
        user = self.context['user']
        
        ride.passengers.add(user)

        #profile
        profile = user.profile
        profile.rides_taken += 1
        profile.save()

        #Membership
        member = self.context['member']
        member.rides_taken += 1
        member.save()

        # Circle
        circle = self.context['circle']
        circle.rides_taken += 1
        circle.save()

        return ride

class EndRideSerializer(serializers.ModelSerializer):
    """End ride serializer"""

    current_time = serializers.DatetimeField()

    class Meta:
        """Meta class"""
        model = Ride
        fields = ('is_active', 'current_time')

    def validate_current_time(self, data):
        """Verify ride have indeed started"""
        #import ipdb; ipdb.set_trace()
        ride = self.context['view'].get_object()
        if data <= ride.departure_date:
            raise serializers.ValidationError('Ride has not started yet')
        return data
    


    


        



