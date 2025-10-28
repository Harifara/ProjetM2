from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import DecashmentValidation, AuditLog, OperationView
import uuid

class DecashmentValidationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_id = uuid.uuid4()

    def test_create_validation(self):
        data = {
            'request_type': 'purchase',
            'request_id': str(uuid.uuid4()),
            'amount': 1000.00,
            'reason': 'Test purchase',
            'requested_by': str(self.user_id),
            'department': 'RH'
        }
        response = self.client.post('/api/coordinateur/validations/', data, format='json')
        self.assertEqual(DecashmentValidation.objects.count(), 1)

    def test_validation_status_choices(self):
        validation = DecashmentValidation.objects.create(
            request_type='payment',
            request_id=uuid.uuid4(),
            amount=500.00,
            requested_by=self.user_id
        )
        self.assertEqual(validation.validation_status, 'en_attente')

class AuditLogTests(TestCase):
    def test_audit_log_creation(self):
        log = AuditLog.objects.create(
            user_id=uuid.uuid4(),
            action_type='TEST_ACTION',
            entity_type='TestEntity',
            entity_id='test-123'
        )
        self.assertIsNotNone(log.id)
        self.assertEqual(log.action_type, 'TEST_ACTION')
