"""Circle membership views"""

# Django Rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

#models
from cride.circles.models import Circle, Membership, Invitation

#Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions.memberships import IsActiveCircleMember, IsSelfMember


#serializers 
from cride.circles.serializers import MembershipModelSerializer, AddMemberSerializer


class MembershipViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):

    """Circle membership view set"""

    serializer_class = MembershipModelSerializer

    def dispatch(self, request, *args, **kwargs): #esta funcion verificara simepre si existe el circulo, que se enuentre disponible en todo el modelo
        """Verify that the circle exists"""
        slug_name = kwargs['slug_name'] #esta parte viene de la url
        self.circle = get_object_or_404(Circle, slug_name = slug_name)
        return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assing permissions based on action."""
        permissions = [IsAuthenticated]
        if self.action != 'create':
            permissions.append(IsActiveCircleMember)
        if self.action == 'invitations':
            permissions.append(IsSelfMember)
        return [p() for p in permissions]

    def get_queryset(self):
        """Return circle members"""

        return Membership.objects.filter(
            circle = self.circle,
            is_active = True
        )
    
    def get_object(self): 
        #este metodo es implementado para obtener el detalle de un miembro de un circulo y como se desea que se traiga por el username y ni por el primarykey
        """Return the circle member by using the user´s username"""
        
        return get_object_or_404(
            Membership,
            user__username=self.kwargs['pk'],
            circle=self.circle,
            is_active=True
        )
    
    def perform_destroy(self, instance):
        #Este metodo se sobreescribe para poder desabilitar el member, si eliminarlo completamente
        """Disable memebership"""
        instance.is_active = False,
        instance.save()
    
    @action(detail=True, methods=['get'])
    def invitations(self, request, *args, **kwargs):
        """Retrieve a member´s invitations breakdown.
        
        will return a list containing all the members that have
        used its ivitations and anothe list containing the
        invitations that haven't being used yet

        enpoint: {{host}}/circles/slugname-circle/members/username/invitations/
        """
        member=self.get_object()
        #a quien ya invito..
        invited_members = Membership.objects.filter( 
            circle=self.circle,
            invited_by=request.user,
            is_active=True
        )
        #invitaciones que no se han usuado
        unused_invitations = Invitation.objects.filter(
            circle=self.circle,
            issued_by=request.user,
            used=False
        ).values_list('code')

        diff = member.remaining_invitations - len(unused_invitations)

        #convertir los codigos a una lista 
        invitations = [x[0] for x in  unused_invitations]
        for i in range(0, diff):
            invitations.append(
                Invitation.objects.create(
                    issued_by=request.user,
                    circle=self.circle
                ).code
            )

        data = {
            'used_invitations': MembershipModelSerializer(invited_members, many=True).data,
            'invitations': invitations
        }
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        """Handle member creation from invitation code"""
        serializer = AddMemberSerializer(
            data=request.data,
            context={'request':request, 'circle':self.circle}
        )
        serializer.is_valid(raise_exception=True)
        member = serializer.save()

        data = self.get_serializer(member).data  #obtiene el serializer del viewset
        return Response(data, status=status.HTTP_201_CREATED)


    