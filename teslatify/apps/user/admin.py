from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User

# unregister Group, not needed
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    view_on_site = False

    list_display = (
        'email',
        'first_name',
        'last_name',
        'username',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at'
    )
    search_fields = (
        'email',
        'username',
        'id'
    )
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser'
    )

    def get_fieldsets(self, request, obj=None):
        # call super first to get the fieldsets
        fieldsets = super().get_fieldsets(request, obj)
        # add the custom fieldsets
        fieldsets += (
            ('Tesla', {
                'fields': (
                    'tesla_access_token',
                    'tesla_refresh_token'
                )
            }),
            ('Spotify', {
                'fields': (
                    'spotify_id',
                    'spotify_access_token',
                    'spotify_refresh_token'
                )
            }),
        )
        return fieldsets
