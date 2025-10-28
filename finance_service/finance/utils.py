from .models import AuditLog, Notification
import requests
from django.conf import settings


def log_audit(user_id, action_type, entity_type=None, entity_id=None, details=None, request=None):
    ip_address = None
    user_agent = None

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    AuditLog.objects.create(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_notification(recipient_id, message, notification_type, related_entity_type=None, related_entity_id=None):
    return Notification.objects.create(
        recipient_id=recipient_id,
        message=message,
        notification_type=notification_type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id
    )


def notify_service(service_name, endpoint, data, method='POST'):
    service_urls = {
        'auth': settings.AUTH_SERVICE_URL,
        'rh': settings.RH_SERVICE_URL,
        'stock': settings.STOCK_SERVICE_URL,
        'coordinateur': settings.COORDINATEUR_SERVICE_URL,
    }

    service_url = service_urls.get(service_name)
    if not service_url:
        raise ValueError(f"Service inconnu: {service_name}")

    url = f"{service_url}/{endpoint.lstrip('/')}"

    try:
        if method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, timeout=10)
        elif method == 'GET':
            response = requests.get(url, params=data, timeout=10)
        else:
            raise ValueError(f"Méthode HTTP non supportée: {method}")

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {'error': str(e)}


def validate_budget(department, category, amount, fiscal_year, month=None):
    from .models import Budget
    from decimal import Decimal

    try:
        if month:
            budget = Budget.objects.get(
                department=department,
                category=category,
                fiscal_year=fiscal_year,
                month=month
            )
        else:
            budget = Budget.objects.get(
                department=department,
                category=category,
                fiscal_year=fiscal_year,
                month__isnull=True
            )

        if budget.remaining_amount >= Decimal(str(amount)):
            return True, budget
        else:
            return False, budget
    except Budget.DoesNotExist:
        return None, None


def update_budget_spent(budget_id, amount):
    from .models import Budget
    from decimal import Decimal

    try:
        budget = Budget.objects.get(id=budget_id)
        budget.spent_amount += Decimal(str(amount))
        budget.save()
        return True
    except Budget.DoesNotExist:
        return False
