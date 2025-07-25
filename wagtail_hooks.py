from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from .models import MqttTopic


class MqttMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.is_staff


@hooks.register('register_admin_menu_item')
def register_mqtt_menu_item():
    return MqttMenuItem(
        _('MQTT Dashboard'), 
        reverse('mqtt:dashboard'), 
        icon_name='radio',
        order=1000
    )


# Register MQTT Topic as snippet
@register_snippet
class MqttTopicSnippet(MqttTopic):
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('description'),
        ], heading="Topic Information"),
        MultiFieldPanel([
            FieldPanel('is_active'),
            FieldPanel('qos'),
        ], heading="Configuration"),
    ]
    
    class Meta:
        proxy = True
        verbose_name = "MQTT Topic"
        verbose_name_plural = "MQTT Topics"


# Add custom CSS for MQTT dashboard
@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="/static/mqtt/css/mqtt-admin.css">'
    )