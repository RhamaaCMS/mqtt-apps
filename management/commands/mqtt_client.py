import time
import signal
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.mqtt.mqtt_client import mqtt_service


class Command(BaseCommand):
    help = 'Run MQTT client service'
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default=getattr(settings, 'MQTT_BROKER_HOST', 'localhost'),
            help='MQTT broker host'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=getattr(settings, 'MQTT_BROKER_PORT', 1883),
            help='MQTT broker port'
        )
        parser.add_argument(
            '--username',
            type=str,
            default=getattr(settings, 'MQTT_BROKER_USERNAME', None),
            help='MQTT broker username'
        )
        parser.add_argument(
            '--password',
            type=str,
            default=getattr(settings, 'MQTT_BROKER_PASSWORD', None),
            help='MQTT broker password'
        )
        parser.add_argument(
            '--auto-subscribe',
            action='store_true',
            help='Automatically subscribe to all active topics in database'
        )
    
    def handle(self, *args, **options):
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.stdout.write(
            self.style.SUCCESS('Starting MQTT client service...')
        )
        
        # Override settings if provided
        if options['host']:
            settings.MQTT_BROKER_HOST = options['host']
        if options['port']:
            settings.MQTT_BROKER_PORT = options['port']
        if options['username']:
            settings.MQTT_BROKER_USERNAME = options['username']
        if options['password']:
            settings.MQTT_BROKER_PASSWORD = options['password']
        
        try:
            # Setup and connect MQTT client
            mqtt_service.setup_client()
            
            if mqtt_service.connect():
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Connected to MQTT broker at {options["host"]}:{options["port"]}'
                    )
                )
                
                # Auto-subscribe to topics if requested
                if options['auto_subscribe']:
                    mqtt_service.subscribe_to_topics()
                    self.stdout.write(
                        self.style.SUCCESS('Subscribed to all active topics')
                    )
                
                # Keep the service running
                self.stdout.write('MQTT client is running. Press Ctrl+C to stop.')
                while self.running:
                    time.sleep(1)
                    
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to connect to MQTT broker')
                )
                sys.exit(1)
                
        except KeyboardInterrupt:
            self.stdout.write('\nReceived interrupt signal')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
        finally:
            self.cleanup()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stdout.write(f'\nReceived signal {signum}')
        self.running = False
    
    def cleanup(self):
        """Cleanup resources"""
        self.stdout.write('Shutting down MQTT client...')
        mqtt_service.disconnect()
        self.stdout.write(
            self.style.SUCCESS('MQTT client stopped successfully')
        )