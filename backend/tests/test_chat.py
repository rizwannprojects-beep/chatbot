import sys
import os
import io
import fitz  # PyMuPDF
import unittest
import uuid

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.users_db import create_user_record
from app.auth.security import hash_password, create_access_token
from app.rag.rag_service import FALLBACK_RESPONSE
from app.database.db_service import get_messages_by_conversation

class TestRAGChatbotPipeline(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.1"

        # Admin for document setup
        admin_email = f"admin_chat_{uuid.uuid4().hex[:6]}@college.edu"
        self.admin = create_user_record(
            name="Chat Admin",
            email=admin_email,
            password_hash=hash_password("adminpass123"),
            role="admin"
        )
        self.admin_token = create_access_token({"sub": self.admin["id"], "role": "admin"})

        # Student A
        student_a_email = f"student_a_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_a = create_user_record(
            name="Student A",
            email=student_a_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_a_token = create_access_token({"sub": self.student_a["id"], "role": "student"})

        # Student B
        student_b_email = f"student_b_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_b = create_user_record(
            name="Student B",
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

    def test_01_end_to_end_grounded_chat(self):
        # 1. Upload & Process official college document with unique keyword
        unique_token = uuid.uuid4().hex[:8]
        pdf_text = f"Special Admissions Criteria {unique_token}: All applicants must submit high school certificates and passport photos by July 15."
        pdf_bytes = self.create_sample_pdf_bytes(pdf_text)
        file_obj = io.BytesIO(pdf_bytes)

        upload_res = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": f"Admissions Guidelines {unique_token}", "category": "Admissions"},
            files={"file": ("admissions_2026.pdf", file_obj, "application/pdf")}
        )
        self.assertEqual(upload_res.status_code, 201)
        doc_id = upload_res.json()["id"]

        proc_res = self.client.post(
            f"/api/documents/{doc_id}/process",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(proc_res.status_code, 200)

        # 2. Student A asks relevant question containing unique keyword
        chat_res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": f"What certificates are required for Special Admissions Criteria {unique_token}?"}
        )
        self.assertEqual(chat_res.status_code, 200)
        data = chat_res.json()
        
        self.assertTrue(data["success"])
        self.assertIn("answer", data)
        self.assertIsNotNone(data["conversation_id"])
        self.assertIsNotNone(data["message_id"])
        self.assertGreaterEqual(len(data["sources"]), 1)
        
        # Verify source metadata integrity
        source_doc_ids = [s["document_id"] for s in data["sources"]]
        self.assertGreaterEqual(len(source_doc_ids), 1)

        # 3. Verify messages saved in database
        conv_id = data["conversation_id"]
        messages = get_messages_by_conversation(conv_id)
        self.assertGreaterEqual(len(messages), 2)  # User question + Assistant response

    def test_02_unknown_question_fallback(self):
        # Set high threshold so unrelated query produces 0 matching chunks
        os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.99"
        
        chat_res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "What is the secret formula for quantum teleportation rocket fuel?"}
        )
        self.assertEqual(chat_res.status_code, 200)
        data = chat_res.json()

        self.assertTrue(data["success"])
        self.assertEqual(data["answer"], FALLBACK_RESPONSE)
        self.assertEqual(len(data["sources"]), 0)

    def test_03_unauthorized_chat_rejection(self):
        response = self.client.post(
            "/api/chat",
            json={"question": "Can I enter without login?"}
        )
        self.assertEqual(response.status_code, 401)

    def test_04_cross_user_conversation_isolation(self):
        # 1. Student A starts conversation
        res_a = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_a_token}"},
            json={"question": "Hello from Student A"}
        )
        conv_id = res_a.json()["conversation_id"]

        # 2. Student B attempts to hijack Student A's conversation thread
        res_b = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_b_token}"},
            json={"question": "Attempted hijack by Student B", "conversation_id": conv_id}
        )
        self.assertEqual(res_b.status_code, 403)
        self.assertIn("Access denied", res_b.json()["detail"])

if __name__ == "__main__":
    unittest.main()
