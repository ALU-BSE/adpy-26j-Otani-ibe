from django.contrib import admin
from .models import SecurityAuditLog

@admin.register(SecurityAuditLog)
class SecurityAuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_performed', 'timestamp')
    list_filter = ('timestamp', 'user')
    readonly_fields = ('user', 'action_performed', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False