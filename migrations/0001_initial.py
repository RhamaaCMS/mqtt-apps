# Generated manually for MQTT app

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MqttConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broker_host', models.CharField(max_length=255)),
                ('broker_port', models.IntegerField(default=1883)),
                ('status', models.CharField(choices=[('connected', 'Connected'), ('disconnected', 'Disconnected'), ('connecting', 'Connecting'), ('error', 'Error')], default='disconnected', max_length=20)),
                ('last_connected', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'MQTT Connection',
                'verbose_name_plural': 'MQTT Connections',
            },
        ),
        migrations.CreateModel(
            name='MqttTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='MQTT topic name (e.g., sensor/temperature)', max_length=255, unique=True)),
                ('description', models.TextField(blank=True, help_text='Description of this topic')),
                ('is_active', models.BooleanField(default=True, help_text='Whether to monitor this topic')),
                ('qos', models.IntegerField(choices=[(0, 'At most once'), (1, 'At least once'), (2, 'Exactly once')], default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'MQTT Topic',
                'verbose_name_plural': 'MQTT Topics',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MqttMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payload', models.TextField(help_text='Message payload')),
                ('qos', models.IntegerField(default=1)),
                ('retain', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='mqtt.mqtttopic')),
            ],
            options={
                'verbose_name': 'MQTT Message',
                'verbose_name_plural': 'MQTT Messages',
                'ordering': ['-received_at'],
            },
        ),
    ]