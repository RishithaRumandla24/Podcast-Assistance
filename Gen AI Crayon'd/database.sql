-- Create extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for podcast memories
CREATE TABLE podcast_memories (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768), -- Using 768-dimensional embeddings (adjust based on your model)
    memory_type TEXT NOT NULL, -- 'theme', 'episode', 'general', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX ON podcast_memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(768),
    match_threshold FLOAT,
    match_count INT,
    user_id_filter TEXT
)
RETURNS TABLE (
    id INT,
    user_id TEXT,
    content TEXT,
    memory_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.user_id,
        m.content,
        m.memory_type,
        m.created_at,
        1 - (m.embedding <=> query_embedding) AS similarity
    FROM podcast_memories m
    WHERE m.user_id = user_id_filter
    AND 1 - (m.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;