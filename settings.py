# MQTT App Settings

# MQTT Broker Configuration
MQTT_BROKER_HOST = 'localhost'
MQTT_BROKER_PORT = 1883
MQTT_BROKER_USERNAME = None
MQTT_BROKER_PASSWORD = None
MQTT_KEEPALIVE = 60

# MQTT Client Configuration
MQTT_AUTO_CONNECT = False  # Auto-connect on Django startup (disabled by default)
MQTT_DEFAULT_QOS = 1
MQTT_RETAIN_MESSAGES = True
MQTT_MAX_STORED_MESSAGES = 1000

# WebSocket Configuration for Real-time Updates
MQTT_WEBSOCKET_ENABLED = True
MQTT_WEBSOCKET_PORT = 8001

# Logging Configuration for MQTT
MQTT_LOG_LEVEL = 'INFO'

# MQTT Client ID (will be auto-generated if not set)
MQTT_CLIENT_ID = None