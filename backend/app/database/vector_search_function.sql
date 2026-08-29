-- Supabase PostgreSQL Vector Similarity Search RPC Function for CampusAI
-- Spec.md Phase 6

CREATE OR REPLACE FUNCTION match_document_chunks (
  query_embedding vector(768),
  match_threshold float DEFAULT 0.10,
  match_count int DEFAULT 4
)
RETURNS TABLE (
  id uuid,
  document_id uuid,
  chunk_index int,
  content text,
  page_number int,
  metadata jsonb,
  similarity float,
  document_title varchar,
  document_category varchar,
  file_name varchar
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    document_chunks.id,
    document_chunks.document_id,
    document_chunks.chunk_index,
    document_chunks.content,
    document_chunks.page_number,
    document_chunks.metadata,
    (1 - (document_chunks.embedding <=> query_embedding))::float AS similarity,
    documents.title AS document_title,
    documents.category AS document_category,
    documents.file_name
  FROM document_chunks
  JOIN documents ON documents.id = document_chunks.document_id
  WHERE document_chunks.embedding IS NOT NULL
    AND (1 - (document_chunks.embedding <=> query_embedding)) >= match_threshold
  ORDER BY document_chunks.embedding <=> query_embedding ASC
  LIMIT match_count;
END;
$$;
