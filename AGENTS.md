# Project Rules
- Use poetry run to run commands as we are using poetry package manager / virtual environment
- Don't make any changes to @n8n/workflows/*
- Refer to below locaitons for important documents about the project
- When making Django code changes, restart the Docker container in detached mode (-d) (volumes are mounted for live updates)
- **Container Management**: Always rebuild and restart the Docker container after making changes to Django code, templates, or static files to ensure updates are properly applied. Use `docker-compose down && docker-compose up --build -d` for full rebuilds.

# Solution Requirements
- Function requirements are documented in @functional-requirements.md
- Non functional requirements are documented in @non-functional-requirements.md

# Feature Roadmap
- Defined in @roadmap.md
- Should also be defined in github issues

# Project Description Usage & How to Run
- defined in @README.md

# MVP Plan
- defined in @mvp_plan.md
- also should be defined in issues in github

# Architecture
- defined in @architecture.md

# Long Running Tasks & Orchestration
- defined in n8n workflows (modular for future agent tool conversion)
- n8n documentation under @n8n/*
- Future: Agentic orchestration with LangChain; MCP client/server integration

# Database Environment Guidelines

## Connection Contexts
This project uses **dual database access patterns** depending on execution context:

### 1. Docker Internal Network (Django Application)
- **Context**: When Django runs inside Docker container
- **Connection String**: `postgresql://postgres:postgres@db:5432/postgres`
- **Host**: `db` (Docker service name linking to local Supabase)
- **Usage**: Django application, n8n workflows, extraction-agent

### 2. Docker Host Direct Connection (Agent Development)
- **Context**: When agents run from Docker host (your laptop)
- **Connection String**: `postgresql://postgres:postgres@127.0.0.1:5432/postgres`
- **Host**: `127.0.0.1` (localhost - local Supabase instance)
- **Usage**: Agent database queries, development scripts, migrations
- **Source**: From `npx supabase start` → Database URL value

## Database Access Commands

### For Agents (Docker Host)
```bash
# Test connection
poetry run python test_universal_db_connection.py --context host

# Quick database queries (RECOMMENDED FOR AGENTS)
poetry run python query_db.py --list-tables
poetry run python query_db.py "SELECT COUNT(*) FROM core_user"
poetry run python query_db.py --describe-table core_user

# Direct database query (for complex queries)
poetry run python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/postgres')
# Your query logic here
"

# Run migrations from host
poetry run python manage.py migrate
```

### For Docker Services
```bash
# Django inside container uses 'db' hostname automatically
# No manual connection string needed for Django operations
```

## Recommended Agent Database Access Pattern

### Simple Queries (Use query_db.py)
```bash
# List all tables
poetry run python query_db.py --list-tables

# Quick count queries
poetry run python query_db.py "SELECT COUNT(*) FROM core_userlist"

# Table structure
poetry run python query_db.py --describe-table core_run
```

### Complex Queries (Use Python script)
```python
import psycopg2

conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/postgres')
cursor = conn.cursor()

# Your complex query here
cursor.execute("""
    SELECT ul.name, COUNT(r.id) as run_count 
    FROM core_userlist ul 
    LEFT JOIN core_run r ON ul.id = r.userlist_id 
    GROUP BY ul.id, ul.name 
    ORDER BY run_count DESC;
""")

results = cursor.fetchall()
for row in results:
    print(f"List: {row[0]}, Runs: {row[1]}")

cursor.close()
conn.close()
```

## Universal Connection Utility
Use `test_universal_db_connection.py` for connection testing:
- `--context host`: Test from Docker host (agents)
- `--context docker`: Test from Docker container
- `--test-all`: Test all connection methods

## Database Inspection Guidelines
- **Always use PostgreSQL** - never use local SQLite
- **For agents**: Use direct connection `postgresql://postgres:postgres@127.0.0.1:5432/postgres`
- **For Django**: Uses container network automatically
- **Migration Verification**: Run `poetry run python manage.py migrate` from host
- **Table Naming**: Django creates tables as `appname_modelname` (e.g., `core_user` table)

## Current Database Status
- **PostgreSQL Version**: 17.6 (Local Supabase from `npx supabase start`)
- **Database Size**: 15 MB
- **Total Tables**: 23 (including Django tables)
- **Schemas**: public, auth, storage, realtime, etc.
- **Supabase Instance**: Local development instance

# N8N Workflow URLS
- Production (Always Running): http://localhost:5678/webhook/scrape
- Test (Only Runs when user says so): http://localhost:5678/webhook-test/scrape
- **Testing Note**: Always use the test endpoint (`/webhook-test/`) when testing n8n workflows to avoid interfering with production runs

# File Size & Modularity Guidelines

## Maximum File Sizes
- **JavaScript modules**: Max 200 lines
- **Django templates**: Max 300 lines  
- **Python services**: Max 400 lines
- **Configuration files**: Max 150 lines

## Single Responsibility Principle
- One primary concern per file
- Split files that exceed size limits
- Use clear, descriptive naming
- Keep related functionality together

## File Organization Standards
- **Templates**: Organize by app and feature (e.g., `core/run_create/partials/`)
- **JavaScript**: Modular by functionality (e.g., `form_validator.js`, `source_manager.js`)
- **Python**: Separate services, models, views, utilities
- **Static files**: Organize by type and usage context

## Code Modularity Requirements
- Functions should be under 50 lines
- Classes should have single responsibilities
- Avoid deeply nested code (>3 levels)
- Use composition over inheritance where appropriate

# Table Editor Implementation
- **Current Implementation**: AG-Grid based table editor (DEFAULT)
- **Legacy Implementation**: HTMX + Alpine.js table editor (DEPRECATED - use ?grid=legacy)
- **Requirements**: Defined in @table_editor_requirements.md
- **Migration Status**: Complete - AG-Grid is now default
- **File Locations**:
  - Active: `core/templates/core/partials/_ag_grid_table.html`
  - Legacy: `core/templates/core/partials/_table_editor.html` (deprecated)
  - Views: `core/templates/core/list_detail_ag_grid.html` (default)
  - Legacy: `core/templates/core/list_detail.html` (fallback)
- **Container Management**: Always rebuild and restart Docker container after making changes to Django code, templates, or static files to ensure updates are properly applied. Use `docker-compose down && docker-compose up --build -d` for full rebuilds.

# Testing Profiles and Channels
For consistent testing, use these profiles/channels with specified parameters:
- **Instagram Profile**: https://www.instagram.com/sabrina_ramonov
- **YouTube Channel**: https://www.youtube.com/@sabrina_ramonov
- **Parameters**: Max results and results size can be max 5, going back 1 month only