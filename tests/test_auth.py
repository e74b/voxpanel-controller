# Patching PATH
import sys
from pathlib import Path
parent_dir = Path().parent.as_posix()
sys.path.append(parent_dir)

from main import app
from fastapi.testclient import TestClient
from auth.tables import User
import jwt, json

client = TestClient(app)

def test_user_signup():
    data = {
            "username": "testuser",
            "password": "password"
            }
    response = client.put("/auth/signup", json=data)
    assert response.status_code == 200
    assert User.exists().where(User.username == data["username"]).run_sync()


    response = client.put("/auth/signup", json=data)
    assert response.status_code == 409

def test_user_login():
    data = {
            "username": "testuser",
            "password": "password"
            }

    response = client.post("/auth/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]
    token_data = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
    assert token_data["username"] == data["username"]
    assert token_data["scopes"] == []
