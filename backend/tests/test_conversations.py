import sys
import os
import io
import fitz  # PyMuPDF
import unittest
import uuid
import time

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.users_db import create_user_record
from app.auth.security import hash_password, create_access_token
from app.database.db_service import get_messages_by_conversation

class TestConversationHistory(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.1"

        # Admin for PDF upload
        admin_email = f"admin_conv_{uuid.uuid4().hex[:6]}@college.edu"
        self.admin = create_user_record(
            name="Conv Admin",
            email=admin_email,
            password_hash=hash_password("adminpass123"),
            role="admin"
        )
        self.admin_token = create_access_token({"sub": self.admin["id"], "role": "admin"})

        # Student A
        student_a_email = f"student_conv_a_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_a = create_user_record(
            name="Conv Student A",
            email=student_a_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_a_token = create_access_token({"sub": self.student_a["id"], "role": "student"})

        # Student B
        student_b_email = f"student_conv_b_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_b = create_user_record(
            name="Conv Student B",
            email=student_b_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_b_token = create_access_token({"sub": self.student_b["id"], "role": "student"})

    def tearDown(self):
        os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.7"

    def create_sample_pdf_bytes(self, text: str) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), text)
        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        return buffer.getvalue()

    def test_01_conversation_creation_and_listing(self):
        # 1. Start new conversation via chat endpoint
        chat_res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "What are the scholarship requirements?"}
        )
        self.assertEqual(chat_res.status_code, 200)
        conv_id = chat_res.json()["conversation_id"]

        # 2. List student A's conversations
        list_res = self.client.get(
            "/api/conversations",
            headers={"Authorization": f"Bearer {self.student_a_token}"}
        )
        self.assertEqual(list_res.status_code, 200)
        convs = list_res.json()
        self.assertGreaterEqual(len(convs), 1)
        self.assertEqual(convs[0]["id"], conv_id)
        self.assertIn("scholarship requirements", convs[0]["title"].lower())

    def test_02_open_and_continue_conversation(self):
        # 1. Start Conversation Thread
        chat_res1 = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "First question in thread"}
        )
        conv_id = chat_res1.json()["conversation_id"]

        # 2. Continue conversation thread
        chat_res2 = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "Follow-up question in thread", "conversation_id": conv_id}
        )
        self.assertEqual(chat_res2.status_code, 200)
        self.assertEqual(chat_res2.json()["conversation_id"], conv_id)

        # 3. Retrieve messages for conversation thread
        msg_res = self.client.get(
            f"/api/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {self.student_a_token}"}
        )
        self.assertEqual(msg_res.status_code, 200)
        messages = msg_res.json()
        self.assertGreaterEqual(len(messages), 4)  # 2 questions + 2 answers

    def test_03_multiple_conversations_ordering(self):
        # Conversation 1
        res1 = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "Conversation 1 Thread"}
        )
        conv_id_1 = res1.json()["conversation_id"]

        time.sleep(0.01)

        # Conversation 2
        res2 = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "Conversation 2 Thread"}
        )
        conv_id_2 = res2.json()["conversation_id"]

        # List conversations
        list_res = self.client.get(
            "/api/conversations",
            headers={"Authorization": f"Bearer {self.student_a_token}"}
        )
        convs = list_res.json()
        # Most recently updated conversation (conv_id_2) must appear first
        self.assertEqual(convs[0]["id"], conv_id_2)

    def test_04_delete_conversation_and_cascading_messages(self):
        # Create conversation
        chat_res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "Temporary conversation to delete"}
        )
        conv_id = chat_res.json()["conversation_id"]

        # Delete conversation
        del_res = self.client.delete(
            f"/api/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {self.student_a_token}"}
        )
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.json()["success"])

        # Verify conversation messages were deleted
        messages = get_messages_by_conversation(conv_id)
        self.assertEqual(len(messages), 0)

    def test_05_cross_user_security_rejections(self):
        # 1. Student A creates conversation
        chat_res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "Private Student A data"}
        )
        conv_id = chat_res.json()["conversation_id"]

        # 2. Student B attempts to open Student A's conversation details -> 403 Forbidden
        get_res = self.client.get(
            f"/api/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {self.student_b_token}"}
        )
        self.assertEqual(get_res.status_code, 403)

        # 3. Student B attempts to read Student A's messages -> 403 Forbidden
        msg_res = self.client.get(
            f"/api/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {self.student_b_token}"}
        )
        self.assertEqual(msg_res.status_code, 403)

        # 4. Student B attempts to delete Student A's conversation -> 403 Forbidden
        del_res = self.client.delete(
            f"/api/conversations/{conv_id}",
            headers={"Authorization": f"Bearer {self.student_b_token}"}
        )
        self.assertEqual(del_res.status_code, 403)

if __name__ == "__main__":
    unittest.main()
