from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class MqttConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mqtt'
    verbose_name = 'MQTT Client'
    
    def ready(self):
        """Initialize MQTT client when Django starts"""
        # Only initialize in production/runserver, not during migrations
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
            
        try:
            # Import here to avoid circular imports
            from django.conf import settings
            
            # Only setup client, don't auto-connect to avoid database access
            auto_connect = getattr(settings, 'MQTT_AUTO_CONNECT', False)
            if auto_connect:
                # Delay the connection to avoid database access during app initialization
                import threading
                def delayed_connect():
                    import time
                    time.sleep(2)  # Wait for Django to fully initialize
                    try:
                        from .mqtt_client import mqtt_service
                        mqtt_service.setup_client()
                        mqtt_service.connect()
                        logger.info("MQTT client auto-connected on startup")
                    except Exception as e:
                        logger.error(f"Failed to auto-connect MQTT client: {e}")
                
                thread = threading.Thread(target=delayed_connect, daemon=True)
                thread.start()
                
        except Exception as e:
            logger.error(f"Failed to initialize MQTT client: {e}")
