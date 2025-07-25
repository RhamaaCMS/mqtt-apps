# MQTT App for Django/Wagtail

Aplikasi MQTT terintegrasi dengan Wagtail admin panel untuk menerima dan mengirim data MQTT.

## Features

- ✅ MQTT Client integration dengan paho-mqtt
- ✅ Wagtail admin panel integration
- ✅ Real-time message monitoring
- ✅ Topic subscription management
- ✅ Message publishing
- ✅ Connection status monitoring
- ✅ Message history storage
- ✅ Django admin integration

## Installation

1. Install dependencies:
```bash
pip install paho-mqtt
```

2. Add to INSTALLED_APPS (sudah otomatis terdeteksi):
```python
# apps.mqtt sudah otomatis ditambahkan oleh auto-discovery
```

3. Run migrations:
```bash
python manage.py migrate mqtt
```

## Configuration

Edit `apps/mqtt/settings.py` untuk konfigurasi MQTT broker:

```python
# MQTT Broker Configuration
MQTT_BROKER_HOST = 'localhost'
MQTT_BROKER_PORT = 1883
MQTT_BROKER_USERNAME = None
MQTT_BROKER_PASSWORD = None
MQTT_KEEPALIVE = 60

# MQTT Client Configuration
MQTT_AUTO_CONNECT = False  # Auto-connect on Django startup
MQTT_DEFAULT_QOS = 1
MQTT_RETAIN_MESSAGES = True
MQTT_MAX_STORED_MESSAGES = 1000
```

## Usage

### 1. Akses Dashboard

- Buka Wagtail admin panel
- Klik menu "MQTT Dashboard" di sidebar
- Atau akses langsung: `/mqtt/dashboard/`

### 2. Connect ke MQTT Broker

1. Klik tombol "Connect" di dashboard
2. Status akan berubah menjadi "Connected" jika berhasil

### 3. Subscribe ke Topic

1. Klik "Subscribe to Topic"
2. Masukkan nama topic (contoh: `sensor/temperature`)
3. Atur QoS level
4. Klik "Subscribe"

### 4. Publish Message

1. Klik "Publish Message"
2. Masukkan topic dan payload
3. Atur QoS dan retain flag
4. Klik "Publish"

### 5. Monitor Messages

- Messages akan muncul real-time di dashboard
- History tersimpan di database
- Bisa diakses via Django admin

## Management Commands

### Start MQTT Client Service

```bash
python manage.py mqtt_client --host localhost --port 1883 --auto-subscribe
```

Options:
- `--host`: MQTT broker host
- `--port`: MQTT broker port  
- `--username`: MQTT username
- `--password`: MQTT password
- `--auto-subscribe`: Auto subscribe to all active topics

## API Endpoints

- `POST /mqtt/connect/` - Connect to MQTT broker
- `POST /mqtt/disconnect/` - Disconnect from MQTT broker
- `POST /mqtt/publish/` - Publish message
- `POST /mqtt/subscribe/` - Subscribe to topic
- `GET /mqtt/status/` - Get connection status
- `GET /mqtt/topic/<id>/messages/` - Get topic messages

## Models

### MqttTopic
- `name`: Topic name (unique)
- `description`: Topic description
- `is_active`: Whether to monitor this topic
- `qos`: Quality of Service level

### MqttMessage
- `topic`: Foreign key to MqttTopic
- `payload`: Message content
- `qos`: Quality of Service level
- `retain`: Retain flag
- `timestamp`: Message timestamp
- `received_at`: When message was received

### MqttConnection
- `broker_host`: MQTT broker host
- `broker_port`: MQTT broker port
- `status`: Connection status
- `last_connected`: Last connection time
- `last_error`: Last error message

## Testing

Run test script:
```bash
python test_mqtt_dashboard.py
```

## Troubleshooting

### Connection Refused Error
- Pastikan MQTT broker running di host/port yang dikonfigurasi
- Default: localhost:1883
- Untuk testing, bisa install Mosquitto MQTT broker

### Database Access Warning
- Warning ini normal saat startup
- MQTT client tidak auto-connect untuk menghindari database access saat initialization

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Pastikan STATIC_URL dan STATIC_ROOT dikonfigurasi dengan benar

## Development

### File Structure
```
apps/mqtt/
├── __init__.py
├── admin.py              # Django admin configuration
├── apps.py              # App configuration
├── models.py            # Database models
├── views.py             # Views for dashboard and API
├── urls.py              # URL routing
├── mqtt_client.py       # MQTT client service
├── wagtail_hooks.py     # Wagtail integration
├── settings.py          # App-specific settings
├── management/
│   └── commands/
│       └── mqtt_client.py  # Management command
├── migrations/          # Database migrations
├── static/mqtt/
│   ├── css/
│   │   └── mqtt-admin.css
│   └── js/
│       └── mqtt-admin.js
└── templates/mqtt/
    └── dashboard.html   # Dashboard template
```

### Adding New Features

1. Extend models in `models.py`
2. Add views in `views.py`
3. Update templates
4. Add URL routes
5. Run migrations

## License

Part of SawitApp project.