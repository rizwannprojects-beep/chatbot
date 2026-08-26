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
from app.database.db_service import get_chunks_for_document, get_document_by_id

class TestDocumentProcessorPipeline(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Admin user for processing
        admin_email = f"admin_proc_{uuid.uuid4().hex[:6]}@college.edu"
        self.admin_user = create_user_record(
            name="Proc Admin",
            email=admin_email,
            password_hash=hash_password("adminpass123"),
            role="admin"
        )
        self.admin_token = create_access_token({"sub": self.admin_user["id"], "role": "admin"})

        # Student user for auth test
        student_email = f"student_proc_{uuid.uuid4().hex[:6]}@college.edu"
        self.student_user = create_user_record(
            name="Proc Student",
            email=student_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_token = create_access_token({"sub": self.student_user["id"], "role": "student"})

    def create_sample_pdf_bytes(self, pages_text: list) -> bytes:
        """Helper to create real multi-page PDF in-memory using PyMuPDF"""
        doc = fitz.open()
        for text in pages_text:
            page = doc.new_page()
            page.insert_text((50, 50), text)
        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        return buffer.getvalue()

    def test_01_single_and_multipage_pdf_processing(self):
        # Create a 3-page PDF
        page1 = "Page 1: CampusAI Admissions Regulations. All students must submit high school transcripts."
        page2 = "Page 2: Examination Policy. End semester exams occur in November and April each academic year."
        page3 = "Page 3: Hostel Rules. Check-in deadline is 10:00 PM for all residential blocks."
        
        pdf_bytes = self.create_sample_pdf_bytes([page1, page2, page3])
        file_obj = io.BytesIO(pdf_bytes)

        # 1. Upload PDF
        upload_res = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Campus Handbook 2026", "category": "General", "description": "Complete student handbook"},
            files={"file": ("campus_handbook.pdf", file_obj, "application/pdf")}
        )
        self.assertEqual(upload_res.status_code, 201)
        doc_id = upload_res.json()["id"]
        self.assertEqual(upload_res.json()["status"], "UPLOADED")

        # 2. Trigger Process Endpoint
        proc_res = self.client.post(
            f"/api/documents/{doc_id}/process",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(proc_res.status_code, 200)
        data = proc_res.json()
        self.assertEqual(data["status"], "COMPLETED")
        self.assertIsNotNone(data["processed_at"])

        # 3. Verify chunks stored in database
        chunks = get_chunks_for_document(doc_id)
        self.assertGreaterEqual(len(chunks), 3)

        # 4. Verify reprocessing (idempotency - no duplicate chunks)
        proc_res2 = self.client.post(
            f"/api/documents/{doc_id}/process",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(proc_res2.status_code, 200)
        chunks_after = get_chunks_for_document(doc_id)
        self.assertEqual(len(chunks_after), len(chunks), "Reprocessing left duplicate chunks in database")

    def test_02_empty_pdf_failure_handling(self):
        # Create empty 1-page PDF with no text
        pdf_bytes = self.create_sample_pdf_bytes([""])
        file_obj = io.BytesIO(pdf_bytes)

        upload_res = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Empty PDF Test", "category": "General"},
            files={"file": ("empty.pdf", file_obj, "application/pdf")}
        )
        doc_id = upload_res.json()["id"]

        # Process empty PDF -> should fail gracefully
        proc_res = self.client.post(
            f"/api/documents/{doc_id}/process",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(proc_res.status_code, 400)
        
        # Verify status is FAILED and error message recorded
        doc = get_document_by_id(doc_id)
        self.assertEqual(doc["status"], "FAILED")
        self.assertIsNotNone(doc["error_message"])

    def test_03_corrupted_pdf_failure_handling(self):
        corrupted_bytes = b"%PDF-1.4 Corrupted fake invalid header text"
        file_obj = io.BytesIO(corrupted_bytes)

        upload_res = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Corrupted Test", "category": "General"},
            files={"file": ("corrupted.pdf", file_obj, "application/pdf")}
        )
        doc_id = upload_res.json()["id"]

        proc_res = self.client.post(
            f"/api/documents/{doc_id}/process",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(proc_res.status_code, 400)
        
        doc = get_document_by_id(doc_id)
        self.assertEqual(doc["status"], "FAILED")

    def test_04_student_authorization_rejection(self):
        # Student cannot trigger document processing
        response = self.client.post(
            "/api/documents/some-doc-id/process",
            headers={"Authorization": f"Bearer {self.student_token}"}
        )
        self.assertEqual(response.status_code, 403)

if __name__ == "__main__":
    unittest.main()
