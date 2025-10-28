from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import DecashmentRequest, Expense, Payment, Budget, Notification
from .utils import create_notification, notify_service
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_pending_decashment_requests():
    threshold = timezone.now() - timedelta(hours=24)
    pending_requests = DecashmentRequest.objects.filter(
        status='pending',
        created_at__lt=threshold
    )

    for request in pending_requests:
        create_notification(
            recipient_id=request.requested_by,
            message=f"Votre demande de décaissement de {request.amount} est en attente depuis plus de 24h.",
            notification_type='DECASHMENT_REMINDER',
            related_entity_type='DecashmentRequest',
            related_entity_id=request.id
        )

    logger.info(f"Vérification des demandes en attente: {pending_requests.count()} rappels envoyés")


@shared_task
def update_budget_alerts():
    budgets = Budget.objects.all()

    for budget in budgets:
        if budget.utilization_percentage >= 90:
            create_notification(
                recipient_id=budget.created_by,
                message=f"Budget {budget.category} pour {budget.department}: {budget.utilization_percentage:.1f}% utilisé",
                notification_type='BUDGET_ALERT',
                related_entity_type='Budget',
                related_entity_id=budget.id
            )

    logger.info(f"Alertes budgétaires vérifiées pour {budgets.count()} budgets")


@shared_task
def generate_monthly_report():
    from datetime import datetime

    current_month = datetime.now().month
    current_year = datetime.now().year

    expenses = Expense.objects.filter(
        date_paid__month=current_month,
        date_paid__year=current_year,
        status='paid'
    )

    total_expenses = sum(e.amount for e in expenses)

    report_data = {
        'month': current_month,
        'year': current_year,
        'total_expenses': str(total_expenses),
        'expense_count': expenses.count(),
        'by_type': {}
    }

    for expense_type, _ in Expense.EXPENSE_TYPES:
        type_expenses = expenses.filter(expense_type=expense_type)
        report_data['by_type'][expense_type] = {
            'count': type_expenses.count(),
            'total': str(sum(e.amount for e in type_expenses))
        }

    logger.info(f"Rapport mensuel généré: {report_data}")
    return report_data


@shared_task
def cleanup_old_notifications():
    threshold = timezone.now() - timedelta(days=30)
    old_notifications = Notification.objects.filter(
        is_read=True,
        read_at__lt=threshold
    )

    count = old_notifications.count()
    old_notifications.delete()

    logger.info(f"Nettoyage: {count} anciennes notifications supprimées")
    return count


@shared_task
def sync_payment_status():
    pending_payments = Payment.objects.filter(status='processing')

    for payment in pending_payments:
        if (timezone.now() - payment.executed_at).days > 3:
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()

            if payment.expense:
                payment.expense.status = 'paid'
                payment.expense.date_paid = timezone.now()
                payment.expense.save()

    logger.info(f"Synchronisation de {pending_payments.count()} paiements")
