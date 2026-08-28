import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database.users_db import get_user_by_email

import uuid

class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        unique_id = uuid.uuid4().hex[:6]
        self.student_email = f"student_{unique_id}@college.edu"
        self.student_password = "password123"
        self.student_name = "Test Student"
        
        self.admin_email = f"admin_{unique_id}@college.edu"
        self.admin_password = "adminpassword123"
        self.admin_name = "Test Admin"

    def test_01_student_registration(self):
        response = self.client.post("/api/auth/register", json={
            "name": self.student_name,
            "email": self.student_email,
            "password": self.student_password,
            "role": "student"
        })
        # If already registered from previous run, accept 201 or 400
        self.assertIn(response.status_code, [201, 400])
        if response.status_code == 201:
            data = response.json()
            self.assertIn("access_token", data)
            self.assertEqual(data["user"]["email"], self.student_email)
            self.assertEqual(data["user"]["role"], "student")

    def test_02_password_not_plaintext(self):
        self.client.post("/api/auth/register", json={
            "name": self.student_name, "email": self.student_email,
            "password": self.student_password, "role": "student"
        })
        user_record = get_user_by_email(self.student_email)
        self.assertIsNotNone(user_record)
        # Password hash must not be plain text
        self.assertNotEqual(user_record["password_hash"], self.student_password)
        # Must be bcrypt hash starting with $2
        self.assertTrue(user_record["password_hash"].startswith("$2"))

    def test_03_student_login_success(self):
        self.client.post("/api/auth/register", json={
            "name": self.student_name, "email": self.student_email,
            "password": self.student_password, "role": "student"
        })
        response = self.client.post("/api/auth/login", json={
            "email": self.student_email,
            "password": self.student_password
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], self.student_email)

    def test_04_login_invalid_credentials(self):
        self.client.post("/api/auth/register", json={
            "name": self.student_name, "email": self.student_email,
            "password": self.student_password, "role": "student"
        })
        response = self.client.post("/api/auth/login", json={
            "email": self.student_email,
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)

    def test_05_get_me(self):
        self.client.post("/api/auth/register", json={
            "name": self.student_name, "email": self.student_email,
            "password": self.student_password, "role": "student"
        })
        login_res = self.client.post("/api/auth/login", json={
            "email": self.student_email,
            "password": self.student_password
        })
        token = login_res.json()["access_token"]
        
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        data = me_res.json()
        self.assertEqual(data["email"], self.student_email)

    def test_06_unauthenticated_protected_route(self):
        me_res = self.client.get("/api/auth/me")
        self.assertEqual(me_res.status_code, 401)

    def test_07_admin_registration_and_authorization(self):
        # Register Admin & Student
        self.client.post("/api/auth/register", json={
            "name": self.admin_name, "email": self.admin_email,
            "password": self.admin_password, "role": "admin"
        })
        self.client.post("/api/auth/register", json={
            "name": self.student_name, "email": self.student_email,
            "password": self.student_password, "role": "student"
        })

        # Login Admin
        admin_login = self.client.post("/api/auth/login", json={
            "email": self.admin_email,
            "password": self.admin_password
        })
        admin_token = admin_login.json()["access_token"]

        # Login Student
        student_login = self.client.post("/api/auth/login", json={
            "email": self.student_email,
            "password": self.student_password
        })
        student_token = student_login.json()["access_token"]

        # Student attempting to access admin route MUST be rejected (403 Forbidden)
        forbidden_res = self.client.get("/api/auth/admin-only", headers={"Authorization": f"Bearer {student_token}"})
        self.assertEqual(forbidden_res.status_code, 403)

        # Admin accessing admin route MUST succeed (200 OK)
        allowed_res = self.client.get("/api/auth/admin-only", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(allowed_res.status_code, 200)

    def test_08_logout(self):
        self.client.post("/api/auth/register", json={
            "name": self.student_name, "email": self.student_email,
            "password": self.student_password, "role": "student"
        })
        login_res = self.client.post("/api/auth/login", json={
            "email": self.student_email,
            "password": self.student_password
        })
        token = login_res.json()["access_token"]
        
        logout_res = self.client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(logout_res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
