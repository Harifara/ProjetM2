from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification_simulation(payload):
    # Simule en log l'envoi de la notification
    logger.info("SIMULATED NOTIFICATION: %s", payload)
    return True
