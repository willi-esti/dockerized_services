-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Main unit of knowledge (could be one idea from a PDF, chat, etc.)
CREATE TABLE knowledge_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,                           -- short human-readable label
  summary TEXT,                                  -- optional description
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()         -- last modified timestamp
);

-- 2. Files that contributed to this knowledge item (PDFs, MDs, etc.)
CREATE TABLE source_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_item_id UUID REFERENCES knowledge_items(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,                       -- local path or URL
  file_type TEXT,                                -- 'pdf', 'md', 'chatlog', etc.
  raw_text TEXT,                                 -- full extracted or generated text
  sha256_hash TEXT,                             -- optional, for exact-dup detection
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()           -- last modified timestamp
);

-- 3. Semantic search chunks for each knowledge item
CREATE TABLE chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_item_id UUID REFERENCES knowledge_items(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  embedding VECTOR(384),
  content_hash TEXT,                             -- optional, for exact-dup detection
  duplicate_of UUID REFERENCES chunks(id),       -- if near-duplicate
  chunk_index INT,                               -- order within the document
  group_id UUID,                                 -- shared for related chunks
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()            -- last modified timestamp
);

-- 4. Tags to categorize knowledge
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()           -- last modified timestamp
);

-- 5. Link knowledge items and tags (many-to-many)
CREATE TABLE knowledge_item_tags (
  knowledge_item_id UUID REFERENCES knowledge_items(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (knowledge_item_id, tag_id)
);


INSERT INTO tags (name, description) VALUES
  ('Workout', 'My workout routines and exercises'),
  ('Nutrition', 'Diet plans and nutritional information'),
  ('Work', 'Work-related knowledge and skills'),
  ('Personal Info', 'Personal information and notes'),
  ('Todo', 'Tasks and to-do items'),
  ('Projects', 'Ongoing projects and their details'),
  ('Ideas', 'Creative ideas and brainstorming notes'),
  ('Learning', 'Learning resources and study materials'),
  ('Health', 'Health-related knowledge and tips'),
  ('Finance', 'Financial information and budgeting tips'),
  ('Diabetes', 'Diabetes management and information'),
  ('Recipes', 'Cooking recipes and culinary tips'),
  ('Travel', 'Travel plans and experiences'),
  ('Books', 'Books I want to read or have read'),
  ('Movies', 'Movies I want to watch or have watched'),
  ('Music', 'Music recommendations and playlists'),
  ('Others', 'Miscellaneous knowledge items');