import sys
import os
import unittest
import uuid

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.db_service import (
    get_db_tables,
    create_document_record,
    add_document_chunk,
    delete_document_record,
    get_chunks_for_document,
    create_conversation_record,
    add_message_record,
    delete_conversation_record,
    get_messages_for_conversation
)
from app.database.users_db import create_user_record, get_user_by_email

class TestDatabaseFoundation(unittest.TestCase):
    def setUp(self):
        email = f"dbtest_{uuid.uuid4().hex[:6]}@college.edu"
        self.user = create_user_record(
            name="DB Test User",
            email=email,
            password_hash="$2b$12$eImiTXuWVxfM37uY4JANjO5E/u0pQ2hXqQ8Y0kQ6V.q1K1K1K1K1K",
            role="student"
        )

    def test_01_all_six_tables_exist(self):
        tables = get_db_tables()
        required_tables = ["users", "documents", "document_chunks", "conversations", "messages", "feedback"]
        for table in required_tables:
            self.assertIn(table, tables, f"Table '{table}' is missing from database schema")

    def test_02_document_chunks_cascading_deletion(self):
        # Create document
        doc = create_document_record(
            title="College Regulations 2026",
            file_name="regulations.pdf",
            uploaded_by=self.user["id"]
        )
        doc_id = doc["id"]

        # Add 2 document chunks
        dummy_embedding = [0.01 * i for i in range(768)]  # 768-dim vector
        chunk1 = add_document_chunk(doc_id, chunk_index=0, content="Section 1: Academic Regulations", page_number=1, embedding=dummy_embedding)
        chunk2 = add_document_chunk(doc_id, chunk_index=1, content="Section 2: Examination Grading", page_number=2, embedding=dummy_embedding)

        # Verify chunks exist
        chunks = get_chunks_for_document(doc_id)
        self.assertEqual(len(chunks), 2)

        # Delete document -> cascading delete chunks
        delete_document_record(doc_id)

        # Verify chunks are automatically removed
        chunks_after = get_chunks_for_document(doc_id)
        self.assertEqual(len(chunks_after), 0)

    def test_03_conversation_messages_cascading_deletion(self):
        # Create conversation
        conv = create_conversation_record(user_id=self.user["id"], title="Academic Regulations Inquiry")
        conv_id = conv["id"]

        # Add user and assistant messages
        msg1 = add_message_record(conv_id, role="user", content="When are the semester exams?")
        msg2 = add_message_record(conv_id, role="assistant", content="Semester exams begin on November 15th according to Page 4.")

        # Verify messages exist
        messages = get_messages_for_conversation(conv_id)
        self.assertEqual(len(messages), 2)

        # Delete conversation -> cascading delete messages
        delete_conversation_record(conv_id)

        # Verify messages are automatically removed
        messages_after = get_messages_for_conversation(conv_id)
        self.assertEqual(len(messages_after), 0)

    def test_04_vector_embedding_dimension(self):
        doc = create_document_record(title="Vector Test", file_name="test.pdf", uploaded_by=self.user["id"])
        dummy_vector = [0.1] * 768  # Verified 768 dimensions for Gemini text-embedding-004
        chunk = add_document_chunk(doc["id"], chunk_index=0, content="Vector Content", embedding=dummy_vector)
        self.assertIsNotNone(chunk["id"])
        delete_document_record(doc["id"])

if __name__ == "__main__":
    unittest.main()
