#!/usr/bin/env python3
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8002/api/coordinateur"
AUTH_URL = "http://localhost:8000/api/auth"

def get_token():
    response = requests.post(
        f"{AUTH_URL}/login/",
        json={
            "username": "coordinateur1",
            "password": "password123"
        }
    )
    if response.status_code == 200:
        return response.json()['access']
    else:
        print(f"Erreur d'authentification: {response.text}")
        return None

def test_create_validation(token):
    print("\n=== Test: Créer une validation ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "request_type": "purchase",
        "request_id": str(uuid4()),
        "amount": 15000.00,
        "reason": "Achat de fournitures de bureau",
        "requested_by": str(uuid4()),
        "department": "RH"
    }
    response = requests.post(f"{BASE_URL}/validations/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get('id') if response.status_code == 201 else None

def test_list_pending(token):
    print("\n=== Test: Lister les demandes en attente ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/validations/pending/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_validate_request(token, validation_id):
    print(f"\n=== Test: Valider la demande {validation_id} ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "validation_status": "validé",
        "comments": "Demande approuvée selon les procédures"
    }
    response = requests.post(
        f"{BASE_URL}/validations/{validation_id}/validate/",
        json=data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_dashboard(token):
    print("\n=== Test: Dashboard statistiques ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/validations/dashboard/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_audit_logs(token):
    print("\n=== Test: Journaux d'audit ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/audit-logs/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Nombre de logs: {data.get('count', 0)}")
        if data.get('results'):
            print(f"Premier log: {json.dumps(data['results'][0], indent=2)}")

def main():
    print("🚀 Test du Service Coordinateur")
    print("=" * 50)

    token = get_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return

    print(f"✅ Token obtenu: {token[:20]}...")

    validation_id = test_create_validation(token)

    test_list_pending(token)

    if validation_id:
        test_validate_request(token, validation_id)

    test_dashboard(token)

    test_audit_logs(token)

    print("\n" + "=" * 50)
    print("✅ Tests terminés")

if __name__ == "__main__":
    main()
