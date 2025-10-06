from django.contrib import admin
from .models import ERPUser

@admin.register(ERPUser)
class ERPUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'created_at']
    search_fields = ['user__username', 'company']
    list_filter = ['created_at']