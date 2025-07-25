import json
import logging
import threading
from datetime import datetime
from typing import Optional, Callable

import paho.mqtt.client as mqtt
from django.conf import settings
from django.utils import timezone

from .models import MqttTopic, MqttMessage, MqttConnection

logger = logging.getLogger(__name__)


class MqttClientService:
    """Service untuk handle MQTT client operations"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.connection_record: Optional[MqttConnection] = None
        self._message_callbacks = []
        self._lock = threading.Lock()
        
    def setup_client(self):
        """Setup MQTT client dengan konfigurasi dari settings"""
        if self.client:
            self.disconnect()
            
        self.client = mqtt.Client()
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_publish = self._on_publish
        
        # Set credentials if provided
        username = getattr(settings, 'MQTT_BROKER_USERNAME', None)
        password = getattr(settings, 'MQTT_BROKER_PASSWORD', None)
        if username and password:
            self.client.username_pw_set(username, password)
            
        return self.client
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            if not self.client:
                self.setup_client()
                
            host = getattr(settings, 'MQTT_BROKER_HOST', 'localhost')
            port = getattr(settings, 'MQTT_BROKER_PORT', 1883)
            keepalive = getattr(settings, 'MQTT_KEEPALIVE', 60)
            
            # Update or create connection record
            self.connection_record, created = MqttConnection.objects.get_or_create(
                broker_host=host,
                broker_port=port,
                defaults={'status': 'connecting'}
            )
            if not created:
                self.connection_record.status = 'connecting'
                self.connection_record.save()
            
            self.client.connect(host, port, keepalive)
            self.client.loop_start()
            
            logger.info(f"Connecting to MQTT broker at {host}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            if self.connection_record:
                self.connection_record.status = 'error'
                self.connection_record.last_error = str(e)
                self.connection_record.save()
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
            
        if self.connection_record:
            self.connection_record.status = 'disconnected'
            self.connection_record.save()
            
        self.is_connected = False
        logger.info("Disconnected from MQTT broker")
    
    def subscribe_to_topics(self):
        """Subscribe to all active topics in database"""
        if not self.is_connected:
            logger.warning("Not connected to MQTT broker")
            return
            
        active_topics = MqttTopic.objects.filter(is_active=True)
        for topic in active_topics:
            self.client.subscribe(topic.name, topic.qos)
            logger.info(f"Subscribed to topic: {topic.name}")
    
    def publish_message(self, topic_name: str, payload: str, qos: int = 1, retain: bool = False) -> bool:
        """Publish message to MQTT topic"""
        if not self.is_connected:
            logger.warning("Not connected to MQTT broker")
            return False
            
        try:
            result = self.client.publish(topic_name, payload, qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published message to {topic_name}")
                return True
            else:
                logger.error(f"Failed to publish message to {topic_name}: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False
    
    def add_message_callback(self, callback: Callable):
        """Add callback untuk handle incoming messages"""
        with self._lock:
            self._message_callbacks.append(callback)
    
    def remove_message_callback(self, callback: Callable):
        """Remove message callback"""
        with self._lock:
            if callback in self._message_callbacks:
                self._message_callbacks.remove(callback)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.is_connected = True
            if self.connection_record:
                self.connection_record.status = 'connected'
                self.connection_record.last_connected = timezone.now()
                self.connection_record.last_error = ''
                self.connection_record.save()
            
            logger.info("Connected to MQTT broker")
            self.subscribe_to_topics()
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            if self.connection_record:
                self.connection_record.status = 'error'
                self.connection_record.last_error = f"Connection failed with code {rc}"
                self.connection_record.save()
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.is_connected = False
        if self.connection_record:
            self.connection_record.status = 'disconnected'
            self.connection_record.save()
        logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic_name = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Get or create topic
            topic, created = MqttTopic.objects.get_or_create(
                name=topic_name,
                defaults={'description': f'Auto-created topic for {topic_name}'}
            )
            
            # Save message
            message = MqttMessage.objects.create(
                topic=topic,
                payload=payload,
                qos=msg.qos,
                retain=msg.retain,
                timestamp=timezone.now()
            )
            
            # Clean up old messages if needed
            max_messages = getattr(settings, 'MQTT_MAX_STORED_MESSAGES', 1000)
            if topic.messages.count() > max_messages:
                old_messages = topic.messages.all()[max_messages:]
                MqttMessage.objects.filter(id__in=[m.id for m in old_messages]).delete()
            
            logger.info(f"Received message from {topic_name}: {payload[:100]}...")
            
            # Call registered callbacks
            with self._lock:
                for callback in self._message_callbacks:
                    try:
                        callback(topic, message)
                    except Exception as e:
                        logger.error(f"Error in message callback: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback when subscribed to topic"""
        logger.info(f"Subscribed to topic with QoS: {granted_qos}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback when message published"""
        logger.info(f"Message published with mid: {mid}")


# Global MQTT client instance
mqtt_service = MqttClientService()