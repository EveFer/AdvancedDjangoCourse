"""Circles admin"""

#Django
from django.contrib import admin

#models
from cride.circles.models import Circle, Membership, Invitation


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Circle Admin"""

    list_display=(
        'slug_name',
        'name',
        'is_public',
        'verified',
        'is_limited',
        'members_limit'
   )
    search_fields=('slug_name', 'name')
    list_filter=(
        'is_public',
        'verified',
        'is_limited'
    )

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Member ship Admmin"""
    list_display=(
        'user',
        'is_admin',
        'used_invitations',
        'remaining_invitations',
        'invited_by',
        'is_active'
    )

    search_fields=('user',)
    list_filter=(
        'is_active',
    )

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):

    list_display=(
        'code',
        'issued_by',
        'used_by',
        'circle',
        'used',
        'used_at'
    )

    search_fields=('code',)

    list_filter=('circle',)