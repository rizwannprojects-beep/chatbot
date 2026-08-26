import sys
import os
import unittest
import uuid

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.users_db import create_user_record
from app.auth.security import hash_password, create_access_token

class TestBonusFeatures(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.1"

        # Admin
        admin_email = f"admin_bonus_{uuid.uuid4().hex[:6]}@college.edu"
        self.admin = create_user_record(
            name="Bonus Admin",
            email=admin_email,
            password_hash=hash_password("adminpass123"),
            role="admin"
        )
        self.admin_token = create_access_token({"sub": self.admin["id"], "role": "admin"})

        # Student A
        student_a_email = f"student_bonus_a_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_a = create_user_record(
            name="Bonus Student A",
            email=student_a_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_a_token = create_access_token({"sub": self.student_a["id"], "role": "student"})

        # Student B
        student_b_email = f"student_bonus_b_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_b = create_user_record(
            name="Bonus Student B",
            email=student_b_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_b_token = create_access_token({"sub": self.student_b["id"], "role": "student"})

    def tearDown(self):
        os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.7"

    def test_01_submit_answer_feedback(self):
        # 1. Student A creates chat message
        chat_res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "What is the fee payment deadline?"}
        )
        self.assertEqual(chat_res.status_code, 200)
        msg_id = chat_res.json()["message_id"]

        # 2. Student A submits feedback
        fb_res = self.client.post(
            "/api/feedback",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"message_id": msg_id, "rating": "helpful", "comment": "Great accurate response!"}
        )
        self.assertEqual(fb_res.status_code, 200)
        self.assertTrue(fb_res.json()["success"])

    def test_02_unauthorized_feedback_rejection(self):
        # 1. Student A creates chat message
        chat_res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "Private Student A question"}
        )
        msg_id = chat_res.json()["message_id"]

        # 2. Student B attempts to submit feedback for Student A's message -> 403 Forbidden
        fb_res = self.client.post(
            "/api/feedback",
            headers={"Authorization": f"Bearer {self.student_b_token}"},
            json={"message_id": msg_id, "rating": "unhelpful"}
        )
        self.assertEqual(fb_res.status_code, 403)

    def test_03_admin_stats_access_and_authorization(self):
        # 1. Admin requests dashboard statistics -> 200 OK
        stats_res = self.client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(stats_res.status_code, 200)
        data = stats_res.json()
        self.assertIn("total_students", data)
        self.assertIn("total_documents", data)
        self.assertIn("completed_documents", data)
        self.assertIn("positive_feedback", data)

        # 2. Student requests admin statistics -> 403 Forbidden
        student_stats_res = self.client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {self.student_a_token}"}
        )
        self.assertEqual(student_stats_res.status_code, 403)

    def test_04_document_filtering_and_search(self):
        docs_res = self.client.get(
            "/api/documents?category=Admissions&status_filter=COMPLETED",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(docs_res.status_code, 200)
        self.assertIsInstance(docs_res.json(), list)

if __name__ == "__main__":
    unittest.main()
