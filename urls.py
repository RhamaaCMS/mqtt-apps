from django.urls import path
from . import views

app_name = 'mqtt'

urlpatterns = [
    path('dashboard/', views.MqttDashboardView.as_view(), name='dashboard'),
    path('connect/', views.mqtt_connect, name='connect'),
    path('disconnect/', views.mqtt_disconnect, name='disconnect'),
    path('publish/', views.mqtt_publish, name='publish'),
    path('subscribe/', views.mqtt_subscribe_topic, name='subscribe'),
    path('status/', views.mqtt_status, name='status'),
    path('topic/<int:topic_id>/messages/', views.mqtt_topic_messages, name='topic_messages'),
]