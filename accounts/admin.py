from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_email_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_email_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'bio', 'profile_picture', 'website', 'twitter', 'linkedin', 'github', 'is_email_verified')
        }),
    )

admin.site.register(User, CustomUserAdmin)
