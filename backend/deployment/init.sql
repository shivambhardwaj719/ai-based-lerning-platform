-- PostgreSQL initialization script
-- Runs once on first container startup via docker-entrypoint-initdb.d/

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";         -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- trigram indexes for LIKE/ILIKE search
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- GIN indexes on scalar types
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- query performance monitoring

-- Create application database if it doesn't exist (handled by POSTGRES_DB env var)
-- This script runs inside the already-created DB

-- Create read-only reporting user for analytics / BI tools
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'reporting_user') THEN
        CREATE ROLE reporting_user WITH LOGIN PASSWORD 'reporting_password_change_me';
    END IF;
END
$$;

-- Grant read-only access on all current and future tables
GRANT CONNECT ON DATABASE ai_learning TO reporting_user;
GRANT USAGE ON SCHEMA public TO reporting_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO reporting_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO reporting_user;

-- Create application user with limited privileges (principle of least privilege)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user WITH LOGIN PASSWORD 'app_password_change_me';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE ai_learning TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- Optimize PostgreSQL settings for workload (applies to current session; use postgresql.conf for persistence)
-- These are advisory; actual tuning depends on instance size

-- Set default timezone
SET timezone = 'UTC';

-- Create partitioned tables for high-volume data

-- submissions table: range-partition by created_at (monthly)
-- NOTE: Alembic manages the base table; partitions are created here for operational setup
-- The actual partitioning setup would be in the first Alembic migration.

-- audit_logs table: range-partition by created_at (monthly)
-- Same note as above

-- Create indexes that benefit from trigram extension (created after extension)
-- These run after Alembic creates the tables; wrapped in DO block to avoid errors if tables don't exist yet

DO $$
BEGIN
    -- Trigram index for fast username search
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        EXECUTE 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_trgm ON users USING gin(username gin_trgm_ops)';
        EXECUTE 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_trgm ON users USING gin(email gin_trgm_ops)';
    END IF;

    -- Trigram index for problem title/description full-text search
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'problems') THEN
        EXECUTE 'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_problems_title_trgm ON problems USING gin(title gin_trgm_ops)';
    END IF;
EXCEPTION WHEN OTHERS THEN
    -- Tables may not exist yet; indexes will be created by Alembic migrations
    RAISE NOTICE 'Skipping trgm indexes: tables not yet created (run Alembic migrations first)';
END
$$;
