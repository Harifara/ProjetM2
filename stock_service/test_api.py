import requests
import json

BASE_URL = "http://localhost:8002/api/stock"
AUTH_URL = "http://localhost:8000/api/auth"

def get_auth_token(username, password):
    response = requests.post(
        f"{AUTH_URL}/login/",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access"]
    return None

def test_stock_endpoints():
    token = get_auth_token("admin", "admin123")

    if not token:
        print("Erreur d'authentification")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("=== Test du Service Stock ===\n")

    print("1. Liste des districts")
    response = requests.get(f"{BASE_URL}/districts/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Data: {json.dumps(response.json(), indent=2)}\n")

    print("2. Créer un district")
    response = requests.post(
        f"{BASE_URL}/districts/",
        headers=headers,
        json={"name": "Antananarivo"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        district_id = response.json()["id"]
        print(f"District créé: {district_id}\n")

        print("3. Créer un magasin")
        response = requests.post(
            f"{BASE_URL}/warehouses/",
            headers=headers,
            json={
                "district": district_id,
                "name": "Magasin Central",
                "location": "Centre-ville Antananarivo"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            warehouse_id = response.json()["id"]
            print(f"Magasin créé: {warehouse_id}\n")

            print("4. Créer une catégorie")
            response = requests.post(
                f"{BASE_URL}/categories/",
                headers=headers,
                json={"name": "Fournitures de bureau"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                category_id = response.json()["id"]
                print(f"Catégorie créée: {category_id}\n")

                print("5. Créer un article de stock")
                response = requests.post(
                    f"{BASE_URL}/items/",
                    headers=headers,
                    json={
                        "warehouse": warehouse_id,
                        "category": category_id,
                        "name": "Stylos BIC",
                        "description": "Boîte de 50 stylos",
                        "sku": "STY-BIC-001",
                        "quantity": 5,
                        "min_threshold": 10,
                        "max_threshold": 100
                    }
                )
                print(f"Status: {response.status_code}")
                print(f"Data: {json.dumps(response.json(), indent=2)}\n")

                if response.status_code == 201:
                    item_id = response.json()["id"]

                    print("6. Articles en stock bas")
                    response = requests.get(f"{BASE_URL}/items/low-stock/", headers=headers)
                    print(f"Status: {response.status_code}")
                    print(f"Articles: {len(response.json())} article(s) en stock bas\n")

                    print("7. Créer une entrée de stock")
                    response = requests.post(
                        f"{BASE_URL}/movements/",
                        headers=headers,
                        json={
                            "stock_item": item_id,
                            "movement_type": "entrée",
                            "quantity": 20,
                            "notes": "Réapprovisionnement"
                        }
                    )
                    print(f"Status: {response.status_code}")
                    print(f"Data: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    test_stock_endpoints()
