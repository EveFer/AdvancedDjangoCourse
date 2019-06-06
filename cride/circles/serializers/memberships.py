"""Membership Serializers"""

#django
from django.utils import timezone

#dajngo rest framework
from rest_framework import serializers

#models
from cride.circles.models import Membership, Invitation

#serializers
from cride.users.serializers import UserModelSerializer


class MembershipModelSerializer(serializers.ModelSerializer):
    """Member model serializer"""
    user = UserModelSerializer(read_only=True) #para anidar informacion al response 
    invited_by = serializers.StringRelatedField() #obtener el username que ha invitado
    joined_at = serializers.DateTimeField(source='created', read_only=True)

    class Meta:
        """Class meta"""
        model = Membership
        fields = (
            'user',
            'is_admin',
            'is_active',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken', 
            'rides_offered',
            'joined_at'
        )
        read_only_fields = (
            'user',
            'used_invitations',
            'invited_by',
            'rides_taken', 
            'rides_offered',
        )

class AddMemberSerializer(serializers.Serializer):
    """Add member serializer.

    Handle the addition of a new member to a circle.
    Circle object must be privided in the context.
    """

    invitation_code = serializers.CharField(min_length=8)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())    #este tipo de serializer no se valida en la entrada del request, sino de manera interna
                                                                                #el valor que toma del default es gracias a que se le a enviado como contexto el request

    def validate_user(self, data):
        """Verify user isn´t already a member"""
        circle = self.context['circle']
        user = data
        #verificar que el usuario no sea miembro
        q = Membership.objects.filter(circle=circle, user=user)
        if q.exists():
            raise serializers.ValidationError('User is already member of this circle')
        return data
    
    def validate_invitation_code(self, data):
        """Verify code exists and that it is related to the circle"""
        #trata de obtener una invitacion con el codigo
        try: 
            invitation = Invitation.objects.get(
                code = data,
                circle= self.context['circle'],
                used=False
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('Invalid invitation code.')
        self.context['invitation'] = invitation
        return data

    def validate(self, data):
        """Verify circle is capable of accepting a new member"""
        circle = self.context['circle']
        if circle.is_limited and circle.members.count() >= circle.members_limit:
            raise serializers.ValidationError('Circle has reached its member limit :(')
        return data

    def create(self, data):
        """Create new circle member"""
        circle = self.context['circle']
        invitation = self.context['invitation']
        user = data['user']
        print(user)
        print(invitation.used)
        now = timezone.now() #fecha en la que la invitacion de utilizo

        #member creation
        member = Membership.objects.create(
            user=user,
            profile=user.profile,
            circle=circle,
            invited_by=invitation.issued_by
        )

        #update Invitation
        invitation.used_by=user
        invitation.used=True
        invitation.used_at=now
        invitation.save()

        #update issuer data
        issuer = Membership.objects.get(user=invitation.issued_by, circle=circle)
        issuer.used_invitations += 1 #cuantas a usuado
        issuer.remaining_invitations -= 1 #cuantos le quedan
        issuer.save()

        return member

