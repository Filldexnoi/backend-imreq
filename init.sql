-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Origin requirements table
CREATE TABLE IF NOT EXISTS origin_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create index on req_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_origin_requirements_req_id ON origin_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_origin_requirements_project_id ON origin_requirements(project_id);

-- Analyzed requirements table
CREATE TABLE IF NOT EXISTS analyzed_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    score VARCHAR(20),
    characteristics JSONB,  -- Changed from TEXT[] to JSONB for consistency
    requirement TEXT NOT NULL,
    evaluation JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_analyzed_requirements_req_id ON analyzed_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_analyzed_requirements_project_id ON analyzed_requirements(project_id);

-- Suggested requirements table
CREATE TABLE IF NOT EXISTS suggested_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    original_requirement TEXT NOT NULL,
    suggested_requirement TEXT NOT NULL,
    original_score VARCHAR(20),
    improvements JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_suggested_requirements_req_id ON suggested_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_suggested_requirements_project_id ON suggested_requirements(project_id);

-- Selected requirements table
CREATE TABLE IF NOT EXISTS selected_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_selected_requirements_req_id ON selected_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_selected_requirements_project_id ON selected_requirements(project_id);

-- Optional: Add unique constraint to prevent duplicate req_id per project
-- Uncomment if you want to enforce uniqueness
-- ALTER TABLE origin_requirements ADD CONSTRAINT uq_origin_req_project UNIQUE (project_id, req_id);
-- ALTER TABLE analyzed_requirements ADD CONSTRAINT uq_analyzed_req_project UNIQUE (project_id, req_id);
-- ALTER TABLE suggested_requirements ADD CONSTRAINT uq_suggested_req_project UNIQUE (project_id, req_id);
-- ALTER TABLE selected_requirements ADD CONSTRAINT uq_selected_req_project UNIQUE (project_id, req_id);
