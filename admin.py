from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MqttTopic, MqttMessage, MqttConnection


@admin.register(MqttTopic)
class MqttTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'qos', 'message_count_display', 'latest_message_display', 'created_at']
    list_filter = ['is_active', 'qos', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'message_count_display', 'latest_message_display']
    
    fieldsets = (
        ('Topic Information', {
            'fields': ('name', 'description')
        }),
        ('Configuration', {
            'fields': ('is_active', 'qos')
        }),
        ('Statistics', {
            'fields': ('message_count_display', 'latest_message_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_count_display(self, obj):
        count = obj.message_count
        if count > 0:
            url = reverse('admin:mqtt_mqttmessage_changelist') + f'?topic__id__exact={obj.id}'
            return format_html('<a href="{}">{} messages</a>', url, count)
        return '0 messages'
    message_count_display.short_description = 'Messages'
    
    def latest_message_display(self, obj):
        latest = obj.latest_message
        if latest:
            return format_html(
                '<span title="{}">{}</span>',
                latest.payload[:200],
                latest.received_at.strftime('%Y-%m-%d %H:%M:%S')
            )
        return 'No messages'
    latest_message_display.short_description = 'Latest Message'


@admin.register(MqttMessage)
class MqttMessageAdmin(admin.ModelAdmin):
    list_display = ['topic', 'payload_preview', 'qos', 'retain', 'timestamp', 'received_at']
    list_filter = ['topic', 'qos', 'retain', 'received_at']
    search_fields = ['topic__name', 'payload']
    readonly_fields = ['topic', 'payload', 'qos', 'retain', 'timestamp', 'received_at', 'payload_formatted']
    date_hierarchy = 'received_at'
    
    fieldsets = (
        ('Message Information', {
            'fields': ('topic', 'timestamp', 'received_at')
        }),
        ('Content', {
            'fields': ('payload_formatted', 'qos', 'retain')
        }),
    )
    
    def payload_preview(self, obj):
        return obj.payload_preview
    payload_preview.short_description = 'Payload Preview'
    
    def payload_formatted(self, obj):
        """Display payload in a formatted way"""
        import json
        try:
            # Try to format as JSON if possible
            parsed = json.loads(obj.payload)
            formatted = json.dumps(parsed, indent=2)
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', formatted)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, display as plain text
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.payload)
    payload_formatted.short_description = 'Payload'
    
    def has_add_permission(self, request):
        # Messages are created automatically, don't allow manual creation
        return False


@admin.register(MqttConnection)
class MqttConnectionAdmin(admin.ModelAdmin):
    list_display = ['broker_host', 'broker_port', 'status', 'last_connected', 'created_at']
    list_filter = ['status', 'broker_host', 'created_at']
    readonly_fields = ['broker_host', 'broker_port', 'status', 'last_connected', 'last_error', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Connection Information', {
            'fields': ('broker_host', 'broker_port', 'status')
        }),
        ('Status Details', {
            'fields': ('last_connected', 'last_error')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Connections are created automatically
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of connection records
        return False


# Custom admin site modifications
admin.site.site_header = "MQTT Dashboard Admin"
admin.site.site_title = "MQTT Admin"
admin.site.index_title = "MQTT Management"