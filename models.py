from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class MqttTopic(models.Model):
    """Model untuk menyimpan MQTT topics yang dimonitor"""
    name = models.CharField(max_length=255, unique=True, help_text="MQTT topic name (e.g., sensor/temperature)")
    description = models.TextField(blank=True, help_text="Description of this topic")
    is_active = models.BooleanField(default=True, help_text="Whether to monitor this topic")
    qos = models.IntegerField(default=1, choices=[(0, 'At most once'), (1, 'At least once'), (2, 'Exactly once')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "MQTT Topic"
        verbose_name_plural = "MQTT Topics"

    def __str__(self):
        return self.name

    @property
    def latest_message(self):
        return self.messages.first()

    @property
    def message_count(self):
        return self.messages.count()


class MqttMessage(models.Model):
    """Model untuk menyimpan MQTT messages yang diterima"""
    topic = models.ForeignKey(MqttTopic, on_delete=models.CASCADE, related_name='messages')
    payload = models.TextField(help_text="Message payload")
    qos = models.IntegerField(default=1)
    retain = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']
        verbose_name = "MQTT Message"
        verbose_name_plural = "MQTT Messages"

    def __str__(self):
        return f"{self.topic.name} - {self.timestamp}"

    @property
    def payload_preview(self):
        """Return first 100 characters of payload"""
        return self.payload[:100] + "..." if len(self.payload) > 100 else self.payload


class MqttConnection(models.Model):
    """Model untuk menyimpan status koneksi MQTT"""
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('connecting', 'Connecting'),
        ('error', 'Error'),
    ]
    
    broker_host = models.CharField(max_length=255)
    broker_port = models.IntegerField(default=1883)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disconnected')
    last_connected = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MQTT Connection"
        verbose_name_plural = "MQTT Connections"

    def __str__(self):
        return f"{self.broker_host}:{self.broker_port} - {self.status}"
