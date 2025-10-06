from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'email', 'created_at']
    search_fields = ['name', 'company', 'email']
    list_filter = ['created_at']
    readonly_fields = ['created_at']