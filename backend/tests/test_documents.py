import sys
import os
import io
import fitz  # PyMuPDF
import unittest
import uuid
from fastapi.testclient import TestClient

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database.users_db import create_user_record
from app.auth.security import hash_password, create_access_token

class TestDocumentManagement(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Create unique Admin User
        admin_email = f"admin_doc_{uuid.uuid4().hex[:6]}@college.edu"
        self.admin_user = create_user_record(
            name="Doc Admin",
            email=admin_email,
            password_hash=hash_password("adminpass123"),
            role="admin"
        )
        self.admin_token = create_access_token({"sub": self.admin_user["id"], "role": "admin"})

        # Create unique Student User
        student_email = f"student_doc_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_user = create_user_record(
            name="Doc Student",
            email=student_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_token = create_access_token({"sub": self.student_user["id"], "role": "student"})

    def create_valid_pdf_bytes(self, text: str) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), text)
        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        return buffer.getvalue()

    def test_01_admin_upload_valid_pdf(self):
        pdf_bytes = self.create_valid_pdf_bytes("Admissions Policy 2026 for CampusAI College Chatbot.")
        file_obj = io.BytesIO(pdf_bytes)
        
        response = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Admissions Policy 2026", "category": "Admissions", "description": "Official admissions criteria"},
            files={"file": ("admissions_policy.pdf", file_obj, "application/pdf")}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Admissions Policy 2026")
        self.assertEqual(data["category"], "Admissions")
        self.assertEqual(data["mime_type"], "application/pdf")
        self.assertEqual(data["status"], "UPLOADED")
        self.assertIsNotNone(data["id"])

        # Store created document id for subsequent tests
        self.__class__.created_doc_id = data["id"]

    def test_02_invalid_file_extension_rejection(self):
        text_content = b"Plain text content"
        file_obj = io.BytesIO(text_content)
        
        response = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Text File Test", "category": "General"},
            files={"file": ("test.txt", file_obj, "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Only PDF", response.json()["detail"])

    def test_03_invalid_mime_type_rejection(self):
        content = b"%PDF-1.4 Test PDF"
        file_obj = io.BytesIO(content)
        
        response = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "MIME Mismatch Test", "category": "General"},
            files={"file": ("test.pdf", file_obj, "image/jpeg")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid MIME type", response.json()["detail"])

    def test_04_oversized_file_rejection(self):
        # Create oversized payload (> 10MB)
        large_content = b"A" * (11 * 1024 * 1024)
        file_obj = io.BytesIO(large_content)

        response = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Oversized PDF Test", "category": "General"},
            files={"file": ("huge.pdf", file_obj, "application/pdf")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("exceeds maximum limit", response.json()["detail"])

    def test_05_filename_sanitization(self):
        pdf_bytes = self.create_valid_pdf_bytes("Sanitized Filename PDF Content.")
        file_obj = io.BytesIO(pdf_bytes)

        response = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Sanitization Test", "category": "General"},
            files={"file": ("../../dangerous_path_filename.pdf", file_obj, "application/pdf")}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertNotIn("..", data["file_name"])
        self.assertNotIn("/", data["file_name"])

    def test_06_student_upload_rejection(self):
        pdf_bytes = self.create_valid_pdf_bytes("Unauthorized Upload")
        file_obj = io.BytesIO(pdf_bytes)

        response = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.student_token}"},
            data={"title": "Student Attempt", "category": "General"},
            files={"file": ("student_file.pdf", file_obj, "application/pdf")}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Admin privileges required", response.json()["detail"])

    def test_07_get_documents_listing(self):
        response = self.client.get(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        docs = response.json()
        self.assertIsInstance(docs, list)
        self.assertGreaterEqual(len(docs), 1)

    def test_08_get_document_details(self):
        doc_id = getattr(self.__class__, "created_doc_id", None)
        self.assertIsNotNone(doc_id)

        response = self.client.get(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], doc_id)
        self.assertEqual(data["status"], "UPLOADED")

    def test_09_process_status_transition(self):
        doc_id = getattr(self.__class__, "created_doc_id", None)
        self.assertIsNotNone(doc_id)

        response = self.client.post(
            f"/api/documents/{doc_id}/process",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "COMPLETED")

    def test_10_student_deletion_rejection(self):
        doc_id = getattr(self.__class__, "created_doc_id", None)
        self.assertIsNotNone(doc_id)

        response = self.client.delete(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        self.assertEqual(response.status_code, 403)

    def test_11_admin_document_deletion(self):
        doc_id = getattr(self.__class__, "created_doc_id", None)
        self.assertIsNotNone(doc_id)

        response = self.client.delete(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        # Verify deletion
        get_res = self.client.get(
            f"/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(get_res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
