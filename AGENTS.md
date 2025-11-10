# Project Rules
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
- **Local Development**: Uses PostgreSQL 15 in Docker container with connection string `postgresql://vibe_user:vibe_pass@postgres:5432/vibe_scraper`
- **Database Inspection**: Always inspect the PostgreSQL database in Docker - never use local SQLite
- **Migration Verification**: Run `python manage.py migrate` in Docker to ensure schema matches models
- **Table Naming**: Django creates tables as `appname_modelname` (e.g., `Location` model → `core_location` table)

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