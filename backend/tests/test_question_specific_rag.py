import sys
import os
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.users_db import create_user_record
from app.auth.security import hash_password, create_access_token
from app.database.db_service import init_db
from app.rag.vector_search import invalidate_vector_cache

class TestQuestionSpecificRAGPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        from seed_comprehensive_college_data import seed_database
        try:
            seed_database()
        except Exception:
            pass
        invalidate_vector_cache()

    def setUp(self):
        self.client = TestClient(app)
        student_email = f"student_rag_{uuid.uuid4().hex[:6]}@college.edu"
        self.student = create_user_record(
            name="RAG Test Student",
            email=student_email,
            password_hash=hash_password("studentpass123"),
            role="student"
        )
        self.student_token = create_access_token({"sub": self.student["id"], "role": "student"})

    def ask(self, question: str):
        res = self.client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {self.student_token}"},
            json={"question": question}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        sources = data.get("sources", [])
        top_score = sources[0].get("similarity", 0.0) if sources else 0.0
        print(f"\n[TEST QUERY] '{question}'")
        print(f"   -> Top Similarity Score: {top_score:.4f} | Retrieved Sources ({len(sources)}): {[s.get('document_title') for s in sources]}")
        print(f"   -> Answer Snippet: {data.get('answer', '')[:120]}...")
        return data

    def test_01_attendance_query_focus(self):
        data = self.ask("What is the minimum attendance required?")
        answer = data["answer"].lower()
        self.assertIn("75%", answer)
        self.assertNotIn("curfew", answer)
        self.assertNotIn("scholarship", answer)

    def test_02_scholarships_query_focus(self):
        data = self.ask("What scholarships are available for students?")
        answer = data["answer"].lower()
        self.assertTrue("scholarship" in answer or "fee" in answer or "grant" in answer)
        self.assertNotIn("curfew", answer)
        self.assertNotIn("series test", answer)

    def test_03_hostel_curfew_query_focus(self):
        data = self.ask("What are the hostel curfew rules?")
        answer = data["answer"].lower()
        self.assertTrue("curfew" in answer or "8:30" in answer or "9:30" in answer or "gate" in answer)
        self.assertNotIn("scholarship", answer)
        self.assertNotIn("revaluation", answer)

    def test_04_examination_query_focus(self):
        data = self.ask("When are semester examinations conducted?")
        answer = data["answer"].lower()
        self.assertTrue("exam" in answer or "test" in answer or "marks" in answer or "semester" in answer)
        self.assertNotIn("curfew", answer)
        self.assertNotIn("hostel", answer)

    def test_05_facilities_query_focus(self):
        data = self.ask("What facilities are available for students?")
        answer = data["answer"].lower()
        self.assertTrue("facility" in answer or "canteen" in answer or "sports" in answer or "gym" in answer or "campus" in answer)

    def test_06_admission_query_focus(self):
        data = self.ask("What is the admission process?")
        answer = data["answer"].lower()
        self.assertTrue("admission" in answer or "b.tech" in answer or "eligibility" in answer or "certificate" in answer)

    def test_07_library_rules_query_focus(self):
        data = self.ask("What are the library rules?")
        answer = data["answer"].lower()
        self.assertTrue("library" in answer or "book" in answer or "borrowing" in answer or "fine" in answer)

    def test_08_attendance_shortage_query_focus(self):
        data = self.ask("What happens if attendance is below the required percentage?")
        answer = data["answer"].lower()
        self.assertTrue("condonation" in answer or "65%" in answer or "fe grade" in answer or "shortage" in answer)

    def test_09_ambiguous_query_clarification(self):
        data = self.ask("What are the rules?")
        answer = data["answer"]
        self.assertTrue("Which rules" in answer or "Attendance" in answer or "Hostel" in answer)
        self.assertEqual(len(data["sources"]), 0)

if __name__ == "__main__":
    unittest.main()
