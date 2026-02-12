from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"Task manager API is running"} 

def test_create_task():
    payload = {
        "title" : "TestTask",
        "description" : "testing task post"
    }
    response = client.post("/tasks/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert "id" in data

def test_read_task():
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)
    if data:
        task = data[0]
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "completed" in task

def test_read_task_filtered():
    response = client.get("/tasks/?completed=true")
    assert response.status_code == 200

    data = response.json()
    for task in data:
        assert task["completed"] is True

def test_read_task_limit():
    response = client.get("/tasks/?limit=1")
    response.status_code == 200
    data = response.json()
    assert len(data) <= 1

def test_read_single_task():
    payload = {
        "title" : "SingleTask",
        "description" : "Testing single task"
    }
    create_response = client.post("/tasks/", json=payload)
    assert create_response.status_code == 200

    created = create_response.json()
    task_id = created["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] is False