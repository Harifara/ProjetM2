from .models import AuditLog


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_audit(user_id, action_type, entity_type=None, entity_id=None, details=None, request=None):
    audit_data = {
        'user_id': user_id,
        'action_type': action_type,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'details': details or {}
    }

    if request:
        audit_data['ip_address'] = get_client_ip(request)
        audit_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

    return AuditLog.objects.create(**audit_data)
