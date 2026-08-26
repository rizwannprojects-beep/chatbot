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
from app.ai.embedding_service import generate_embedding, generate_batch_embeddings, EMBEDDING_DIMENSION
from app.rag.vector_search import search_similar_chunks, cosine_similarity
from app.database.db_service import get_chunks_for_document

class TestEmbeddingsAndVectorSearch(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Admin user
        admin_email = f"admin_vec_{uuid.uuid4().hex[:6]}@college.edu"
        self.admin_user = create_user_record(
            name="Vector Admin",
            email=admin_email,
            password_hash=hash_password("adminpass123"),
            role="admin"
        )
        self.admin_token = create_access_token({"sub": self.admin_user["id"], "role": "admin"})

    def create_sample_pdf_bytes(self, text: str) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), text)
        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        return buffer.getvalue()

    def test_01_single_chunk_embedding_dimension(self):
        vector = generate_embedding("Sample college academic regulation text.")
        self.assertIsInstance(vector, list)
        self.assertEqual(len(vector), EMBEDDING_DIMENSION)
        self.assertEqual(EMBEDDING_DIMENSION, 768)

    def test_02_batch_chunk_embeddings(self):
        texts = ["Admissions criteria 2026", "Hostel check-in rules and curfew", "End semester exam grading policy"]
        vectors = generate_batch_embeddings(texts)
        self.assertEqual(len(vectors), 3)
        for vec in vectors:
            self.assertEqual(len(vec), 768)

    def test_03_cosine_similarity_math(self):
        v1 = [1.0] + [0.0] * 767
        v2 = [1.0] + [0.0] * 767
        v3 = [0.0] * 767 + [1.0]
        
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0, places=4)
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0, places=4)

    def test_04_document_embedding_storage_and_vector_search(self):
        pdf_text = "Hostel Rules: Night curfew is at 10:00 PM. Visitors must sign the hostel register at reception."
        pdf_bytes = self.create_sample_pdf_bytes(pdf_text)
        file_obj = io.BytesIO(pdf_bytes)

        # 1. Upload Document
        upload_res = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Hostel Regulations Manual", "category": "Hostel"},
            files={"file": ("hostel_rules.pdf", file_obj, "application/pdf")}
        )
        self.assertEqual(upload_res.status_code, 201)
        doc_id = upload_res.json()["id"]

        # 2. Process Document (Generates embeddings & saves to document_chunks)
        proc_res = self.client.post(
            f"/api/documents/{doc_id}/process",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(proc_res.status_code, 200)

        # 3. Vector Similarity Search
        query = "What is the hostel night curfew time?"
        results = search_similar_chunks(query, top_k=3, similarity_threshold=0.1)

        self.assertGreaterEqual(len(results), 1)
        top_match = results[0]
        self.assertIn("content", top_match)
        self.assertIn("similarity", top_match)
        self.assertIn("document_title", top_match)
        self.assertEqual(top_match["document_title"], "Hostel Regulations Manual")
        self.assertGreater(top_match["similarity"], 0.0)

    def test_05_top_k_limiting_and_similarity_threshold(self):
        pdf_text = "Exam Schedule: Final semester exams start on December 1st."
        pdf_bytes = self.create_sample_pdf_bytes(pdf_text)
        file_obj = io.BytesIO(pdf_bytes)

        upload_res = self.client.post(
            "/api/documents",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            data={"title": "Exam Timetable", "category": "Examination"},
            files={"file": ("exam_schedule.pdf", file_obj, "application/pdf")}
        )
        doc_id = upload_res.json()["id"]
        self.client.post(f"/api/documents/{doc_id}/process", headers={"Authorization": f"Bearer {self.admin_token}"})

        # Test top_k constraint = 1
        results_k1 = search_similar_chunks("When do exams start?", top_k=1, similarity_threshold=0.0)
        self.assertLessEqual(len(results_k1), 1)

        # Test impossible similarity threshold = 0.9999
        results_high = search_similar_chunks("Unrelated random question", top_k=4, similarity_threshold=0.9999)
        self.assertEqual(len(results_high), 0)

if __name__ == "__main__":
    unittest.main()
