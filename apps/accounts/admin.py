from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'created_at']
    
    # Define fieldsets completely (don't use UserAdmin.fieldsets +)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Profile Info', {'fields': ('bio', 'profile_picture', 'website')}),
    )
    readonly_fields = ['date_joined', 'last_login']

admin.site.register(CustomUser, CustomUserAdmin)