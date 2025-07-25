import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.core.paginator import Paginator

from .models import MqttTopic, MqttMessage, MqttConnection
from .mqtt_client import mqtt_service


@method_decorator(staff_member_required, name='dispatch')
class MqttDashboardView(TemplateView):
    """Main MQTT dashboard view"""
    template_name = 'mqtt/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get connection status
        connection = MqttConnection.objects.first()
        
        # Get topics with latest messages
        topics = MqttTopic.objects.all()
        
        # Get recent messages
        recent_messages = MqttMessage.objects.select_related('topic')[:20]
        
        context.update({
            'connection': connection,
            'topics': topics,
            'recent_messages': recent_messages,
            'is_connected': mqtt_service.is_connected,
        })
        
        return context


@staff_member_required
@require_http_methods(["POST"])
@csrf_exempt
def mqtt_connect(request):
    """Connect to MQTT broker"""
    try:
        success = mqtt_service.connect()
        return JsonResponse({
            'success': success,
            'message': 'Connected to MQTT broker' if success else 'Failed to connect'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@staff_member_required
@require_http_methods(["POST"])
@csrf_exempt
def mqtt_disconnect(request):
    """Disconnect from MQTT broker"""
    try:
        mqtt_service.disconnect()
        return JsonResponse({
            'success': True,
            'message': 'Disconnected from MQTT broker'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@staff_member_required
@require_http_methods(["POST"])
@csrf_exempt
def mqtt_publish(request):
    """Publish message to MQTT topic"""
    try:
        data = json.loads(request.body)
        topic_name = data.get('topic')
        payload = data.get('payload')
        qos = data.get('qos', 1)
        retain = data.get('retain', False)
        
        if not topic_name or payload is None:
            return JsonResponse({
                'success': False,
                'message': 'Topic and payload are required'
            })
        
        success = mqtt_service.publish_message(topic_name, payload, qos, retain)
        
        return JsonResponse({
            'success': success,
            'message': 'Message published successfully' if success else 'Failed to publish message'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@staff_member_required
@require_http_methods(["GET"])
def mqtt_topic_messages(request, topic_id):
    """Get messages for a specific topic"""
    try:
        topic = get_object_or_404(MqttTopic, id=topic_id)
        messages = topic.messages.all()
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(messages, 50)
        page_obj = paginator.get_page(page)
        
        messages_data = []
        for message in page_obj:
            messages_data.append({
                'id': message.id,
                'payload': message.payload,
                'qos': message.qos,
                'retain': message.retain,
                'timestamp': message.timestamp.isoformat(),
                'received_at': message.received_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_number': page_obj.number,
            'total_pages': paginator.num_pages,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@staff_member_required
@require_http_methods(["POST"])
@csrf_exempt
def mqtt_subscribe_topic(request):
    """Subscribe to a new MQTT topic"""
    try:
        data = json.loads(request.body)
        topic_name = data.get('topic')
        description = data.get('description', '')
        qos = data.get('qos', 1)
        
        if not topic_name:
            return JsonResponse({
                'success': False,
                'message': 'Topic name is required'
            })
        
        # Create or update topic
        topic, created = MqttTopic.objects.get_or_create(
            name=topic_name,
            defaults={
                'description': description,
                'qos': qos,
                'is_active': True
            }
        )
        
        if not created:
            topic.is_active = True
            topic.qos = qos
            topic.description = description
            topic.save()
        
        # Subscribe if connected
        if mqtt_service.is_connected:
            mqtt_service.client.subscribe(topic_name, qos)
        
        return JsonResponse({
            'success': True,
            'message': f'Subscribed to topic: {topic_name}',
            'topic_id': topic.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@staff_member_required
@require_http_methods(["GET"])
def mqtt_status(request):
    """Get current MQTT connection status"""
    try:
        connection = MqttConnection.objects.first()
        topics_count = MqttTopic.objects.filter(is_active=True).count()
        messages_count = MqttMessage.objects.count()
        
        return JsonResponse({
            'success': True,
            'is_connected': mqtt_service.is_connected,
            'connection': {
                'status': connection.status if connection else 'disconnected',
                'broker_host': connection.broker_host if connection else '',
                'broker_port': connection.broker_port if connection else 1883,
                'last_connected': connection.last_connected.isoformat() if connection and connection.last_connected else None,
                'last_error': connection.last_error if connection else '',
            },
            'stats': {
                'active_topics': topics_count,
                'total_messages': messages_count,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })
