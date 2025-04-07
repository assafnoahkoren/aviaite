-- Create enum for supported file types
CREATE TYPE file_type AS ENUM ('application/pdf');

-- Table for storing documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type file_type NOT NULL,
    file_size BIGINT NOT NULL,
    created_time TIMESTAMP NOT NULL,
    modified_time TIMESTAMP NOT NULL,
    -- PDF specific metadata (nullable)
    pdf_title TEXT,
    pdf_author TEXT,
    pdf_subject TEXT,
    pdf_creator TEXT,
    pdf_page_count INTEGER,
    -- Processing metadata
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    embedding_model TEXT,
    UNIQUE (file_path)
);

-- Table for storing document pages (for PDFs)
CREATE TABLE IF NOT EXISTS document_pages (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    page_text_length INTEGER NOT NULL,
    page_size JSONB, -- Store PDF mediabox info
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (document_id, page_number)
);

-- Table for storing text chunks with their metadata
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT NOT NULL,
    metadata JSONB NOT NULL,  -- All metadata including document, page, and chunk info
    embedding vector(1536),   -- Nullable for now since we're not generating embeddings yet
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing chunk-page relationships and positions
CREATE TABLE IF NOT EXISTS chunk_pages (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    page_id INTEGER NOT NULL REFERENCES document_pages(id) ON DELETE CASCADE,
    start_in_page INTEGER NOT NULL,
    end_in_page INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (chunk_id, page_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);
CREATE INDEX IF NOT EXISTS idx_chunks_metadata ON chunks USING gin (metadata);  -- For querying JSONB fields
CREATE INDEX IF NOT EXISTS idx_chunks_source_file ON chunks((metadata->>'source_file_path'));
CREATE INDEX IF NOT EXISTS idx_chunk_pages_chunk_id ON chunk_pages(chunk_id);
CREATE INDEX IF NOT EXISTS idx_chunk_pages_page_id ON chunk_pages(page_id);

-- Create index for vector similarity search (for when we add embeddings)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Function to search for similar chunks (will be useful when we add embeddings)
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(1536),
    similarity_threshold float,
    max_results integer
)
RETURNS TABLE (
    chunk_id integer,
    chunk_text text,
    metadata jsonb,
    similarity float
)
LANGUAGE sql
AS $$
    SELECT 
        id as chunk_id,
        chunk_text,
        metadata,
        1 - (embedding <=> query_embedding) as similarity
    FROM chunks
    WHERE embedding IS NOT NULL 
    AND 1 - (embedding <=> query_embedding) > similarity_threshold
    ORDER BY similarity DESC
    LIMIT max_results;
$$; 