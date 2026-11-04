# Intergration tests

from sqlmodel import delete

from app.models import Service, Status

MISSING_ID = 99999 # test DB table is empty when tests run so MISSING_ID being 99999 will trigger id not found error

# Endpoint success test paths

def test_get_services(db_session, client):
    # delete all rows in service table, add 2 services to the service table, make HTTP request and assert the expected response 
    db_session.exec(delete(Service))
    db_session.commit()

    db_session.add_all([
        Service(
            name="Payments API",
            description="Handles payment processing",
            owner="Payments Team",
            status=Status.operational,
        ),
        Service(
            name="Auth API",
            description="Handles user authentication",
            owner="Identity Team",
            status=Status.degraded,
        ),
    ])

    db_session.commit()

    # make GET request and verify response
    response = client.get("/api/services/")
    
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert {service["name"] for service in data} == {
        "Payments API",
        "Auth API",
    }
    
    
def test_get_service(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
    
    service = Service(
        name="Payments API",
        description="Handles payment processing",
        owner="Payments Team",
        status=Status.operational,
    )
    
    db_session.add(service)
    db_session.commit()
    
    service_id = service.id
    
    response = client.get(f"/api/services/{service_id}")

    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == service_id
    assert data["name"] == "Payments API"
    
    
    
def test_create_service(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
    
    payload = {
        "name": "Payments API",
        "description": "Handles payment processing",
        "owner": "Payments Team",
        "status": "operational"
    }
    
    response = client.post("/api/services/", json=payload)

    assert response.status_code == 201
    
    # verify what the client recieved
    data = response.json()
    assert data["id"] is not None
    for key, value in payload.items():
        assert data[key] == value
    
    # verify the new information in the DB
    new_service = db_session.get(Service, data["id"])
    assert new_service is not None
    assert new_service.name == payload["name"]
    assert new_service.description == payload["description"]
    assert new_service.owner == payload["owner"]
    assert new_service.status == payload["status"]
    
    
def test_update_service(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
        
    service = Service(
        name="Payments API",
        description="Handles payment processing",
        owner="Payments Team",
        status=Status.operational,
    )
    
    db_session.add(service)
    db_session.commit()
    
    payload = {
        "name": "Authentication API",
        "description": "Handles authentication",
        "owner": "Auth Team",
    }
    
    service_id = service.id
    
    response = client.patch(f"/api/services/{service_id}", json=payload)

    assert response.status_code == 200
    
    # verify what the client recieved
    data = response.json()
    assert data["id"] == service_id
    assert data["name"] == payload["name"]

    # verify the updated information in the DB
    db_session.refresh(service)
    assert service.name == payload["name"]
    assert service.description == payload["description"]
    assert service.owner == payload["owner"]
    assert service.status == Status.operational


def test_delete_service(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
        
    service = Service(
        name="Payments API",
        description="Handles payment processing",
        owner="Payments Team",
        status=Status.operational,
    )
    
    db_session.add(service)
    db_session.commit()
    
    service_id = service.id
    
    response = client.delete(f"/api/services/{service_id}")
    assert response.content == b"" # delete request should have no body

    assert response.status_code == 204
    
    db_session.expire_all() # can't use db_session.refresh(service) because it expects the row to still be there, useful for the update test, but not the delete test
    assert db_session.get(Service, service_id) is None
    
    
# Endpoint error test paths

def test_get_service_not_found(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
    
    response = client.get(f"/api/services/{MISSING_ID}") 
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"
    
    
def test_update_service_not_found(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
    
    payload = {
        "name": "Authentication API",
        "description": "Handles authentication",
        "owner": "Auth Team",
    }
    
    response = client.patch(f"/api/services/{MISSING_ID}", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"
    
    
def test_update_service_empty_body(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
    
    service = Service(
        name="Payments API",
        description="Handles payment processing",
        owner="Payments Team",
        status=Status.operational,
    )
    db_session.add(service)
    db_session.commit()
    
    service_id = service.id
    
    payload = {}
    
    response = client.patch(f"/api/services/{service_id}", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields provided for update"
    
    # verify the row in the DB is unchanged
    db_session.refresh(service)
    assert service.name == "Payments API"
    assert service.description == "Handles payment processing"
    assert service.owner == "Payments Team"
    assert service.status == Status.operational


def test_delete_service_not_found(db_session, client):
    db_session.exec(delete(Service))
    db_session.commit()
    
    response = client.delete(f"/api/services/{MISSING_ID}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"