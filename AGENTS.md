# Project Rules
- Don't make any changes to @n8n/workflows/*
- Refer to below locaitons for important documents about the project

# Solution Requirements
- Function requirements are documented in @functional-requirements.md
- Non functional requirements are documented in @non-functional-requirements.md

# Feature Roadmap
- Defined in @roadmap.md
- Should also be defined in github issues

# Project Description Usage & How to Run
- defined in @README.md

# Proof Of Concept Plan
- defined in @poc_plan.md 
- also should be defined in issues in github

# Architecture
- defined in @architecture.md

# Long Running Tasks & Orchestration
- defined in n8n workflows
- n8n documentation under @n8n/*

# Database Environment Guidelines
- **Local Development**: Uses PostgreSQL 15 in Docker container with connection string `postgresql://vibe_user:vibe_pass@postgres:5432/vibe_scraper`
- **Database Inspection**: Always inspect the PostgreSQL database in Docker - never use local SQLite
- **Migration Verification**: Run `python manage.py migrate` in Docker to ensure schema matches models
- **Table Naming**: Django creates tables as `appname_modelname` (e.g., `Location` model → `core_location` table)

# N8N Workflow URLS
- Production (Always Running): http://localhost:5678/webhook/scrape
- Test (Only Runs when user says so): http://localhost:5678/webhook-test/scrape