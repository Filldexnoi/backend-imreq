-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    requirement_template VARCHAR(50),
    reference_files JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- Origin requirements table
CREATE TABLE IF NOT EXISTS origin_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_origin_requirements_req_id ON origin_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_origin_requirements_project_id ON origin_requirements(project_id);

-- Analyzed requirements table
CREATE TABLE IF NOT EXISTS analyzed_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    score VARCHAR(20),
    characteristics TEXT[],
    requirement TEXT NOT NULL,
    evaluation JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_analyzed_requirements_req_id ON analyzed_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_analyzed_requirements_project_id ON analyzed_requirements(project_id);

-- Suggested requirements table
CREATE TABLE IF NOT EXISTS suggested_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    original_requirement TEXT NOT NULL,
    suggested_requirement TEXT,
    original_score VARCHAR(20),
    improvements JSONB,
    is_split BOOLEAN DEFAULT FALSE,
    split_requirements JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_suggested_requirements_req_id ON suggested_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_suggested_requirements_project_id ON suggested_requirements(project_id);

-- Selected requirements table
CREATE TABLE IF NOT EXISTS selected_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id VARCHAR(50) NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    module VARCHAR(255),
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_selected_requirements_req_id ON selected_requirements(req_id);
CREATE INDEX IF NOT EXISTS idx_selected_requirements_project_id ON selected_requirements(project_id);
