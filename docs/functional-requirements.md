# Functional Requirements

## Overview
The Vibe Code IG Scraper SaaS allows users to extract and curate structured data from social media profiles into personalized collections. While currently focused on location-based recommendations for Google Maps integration, the platform is designed to be flexible for various data extraction use cases including lead generation, investment research, and custom analytics.

## User Stories

### User Authentication & Management
- **As a user**, I want to sign up/login with Google or Apple so that I can access my personalized account.
- **As a user**, I want to manage my profile so that I can update my preferences and view my subscription status.

### Social Media Profile Management
- **As a user**, I want to add public social media profiles (e.g., Instagram, TikTok) so that I can specify sources for data extraction.
- **As a user**, I want to view and edit my added profiles so that I can keep them up-to-date.
- **As a user**, I want agents to dynamically select optimal scraping tools based on profile type and cost.

### Data Scraping & Processing
- **As a user**, I want to trigger scraping of specified profiles so that entities are extracted from posts using LLM processing.
- **As a user**, I want the agent to automatically extract and validate entities according to my specifications (e.g., locations with geocoding, leads with contact info, etc.) so that I don't have to do manual work.
- **As a user**, I want to enable/disable AI extraction so that I can choose whether to run LLM processing on scraped data.
- **As a user**, I want to provide custom system prompts for entity extraction so that I can tailor scraping behavior to different use cases.
- **As a user**, I want agents to validate and sanitize my prompts to prevent malicious use.
- **As a user**, I want the agent to handle both web UI storage and MCP server responses with appropriate formatting.
- **As a user**, I want scraped data organized by platform (e.g., {'instagram': [...], 'tiktok': [...]}) for better filtering and multi-platform support.

### Curation & Organization
- **As a user**, I want to review extracted entities in a generic list view so that I can add notes, descriptions, and categories.
- **As a user**, I want to create and manage multiple curated collections so that I can organize entities by theme or purpose (e.g., travel spots, business leads).
- **As a user**, I want to edit or delete entities/collections so that I can maintain accurate information.

### Export & Integration
- **As a user**, I want to export curated collections in CSV or JSON formats from the web UI so that I can use them in other tools and applications.
- **As an MCP client**, I want the agent to return data in multiple formats (file, markdown, JSON/CSV message) based on the request context.

### Data Visualization & Interaction
- **As a user**, I want to view raw scraped data in an expandable JSON viewer with syntax highlighting and search, so that I can inspect large datasets easily.

### Payments & Subscriptions
- **As a user**, I want to view available subscription plans so that I can choose the right tier.
- **As a user**, I want to subscribe via Stripe checkout so that I can access premium features.
- **As a user**, I want to manage my subscription (upgrade/downgrade/cancel) so that I can control my billing.
- **As a user**, I want to see cost estimates for scraping operations before confirming so that I can manage expenses.
- **As a user**, I want dynamic pricing based on actual API usage and agent decisions.

### Metrics & Analytics (Admin/Internal)
- **As an admin**, I want to track user metrics (signups, usage, conversions) so that I can monitor business health.
- **As an admin**, I want to monitor system performance and costs so that I can optimize operations.

### Workflow Modularity
- **As a developer**, I want n8n workflows to be modular with reusable sub-workflows for scraping, extraction, geocoding, and storage, so that maintenance and testing are simplified.

## Features by Component

### Frontend (Django Templates)
- Login/signup page with OAuth buttons.
- Dashboard for profile management and list overview.
- Profile addition/editing forms.
- Curation interface: list locations, add/edit metadata.
- Export buttons with download links.
- Subscription page with Stripe buy buttons.

### Backend (Django)
- User model with Supabase integration.
- Profile and flexible entity models (JSONB-based for adaptability).
- Run model with enable_extraction toggle for optional LLM processing.
- API endpoints for triggering agents and handling MCP requests.
- Generic entity list views with CRUD operations.
- Stripe webhook handlers for subscription events with usage tracking.
- Prompt sanitization and validation for user inputs.
- Interactive JSON viewer for raw scraped data inspection.

### External Integrations
- Supabase: Auth, DB, Analytics.
- n8n: Modular workflow orchestration with sub-workflows for scraping, extraction, geocoding, and storage.
- Apify: Scraping actors as agent-callable tools with cost querying.
- Stripe: Payment processing with dynamic pricing.
- Mapbox: Geocoding API for location validation.
- Google Maps: My Maps export.
- LangChain: Advanced agent framework (future).
- MCP: Client/server for agent integrations.

### Security & Validation
- **URL Validation**: Backend validates user-submitted profile URLs against domain whitelist (instagram.com, tiktok.com) and format requirements.
- **Input Sanitization**: All user inputs sanitized; length limits enforced.
- **Prompt Sanitization**: User-provided system prompts validated for malicious content using AI guardrails.
- **Rate Limiting**: Per-user limits on scraping requests and API calls.
- **Authentication Enforcement**: All scraping triggers require authenticated users.
- **Tier-Based Limits**: Free tier limited to 10 locations/profile, premium to 50+; enforced server-side with dynamic cost checks.

### Backend API Requirements
- **Scraping Trigger Endpoint**: POST /api/scrape/ - accepts profile URLs and extraction specifications, validates user tier, triggers agent for scraping + LLM extraction + validation.
- **Entity Management**: CRUD endpoints for viewing/editing extracted entities in generic list format.
- **Export Endpoint**: GET /api/export/ - generates CSV/JSON files based on curated collections.
- **MCP Endpoint**: Handles MCP server requests, delegates to agent, returns formatted responses.
- **Prompt Management**: Endpoints for submitting and validating custom system prompts.

## Acceptance Criteria
- All user stories must have corresponding UI/API implementations.
- Data must be securely stored and tied to user accounts.
- Entity extraction via LLM must be accurate and validated.
- Web UI shows generic entity lists with CSV/JSON export.
- MCP server returns data in appropriate formats (file/markdown/message).
- Subscriptions must enforce feature limits with dynamic cost estimation.
- URL validation prevents SSRF and malicious scraping.
- All API endpoints require authentication and respect user tiers.
- User prompts are sanitized to prevent malicious use.
- Agents handle both web UI and MCP contexts seamlessly.
- The system must be adaptable to different entity extraction schemas.

## File Size & Modularity Requirements

### Maximum File Sizes
- **JavaScript modules**: Max 200 lines
- **Django templates**: Max 300 lines  
- **Python services**: Max 400 lines
- **Configuration files**: Max 150 lines

### Code Organization Standards
- **Single Responsibility**: One primary concern per file
- **Function Length**: Functions should be under 50 lines
- **Class Scope**: Classes should have focused responsibilities
- **Nesting Limits**: Avoid deeply nested code (>3 levels)
- **Modular Design**: Use composition over inheritance where appropriate

### File Structure Guidelines
- **Templates**: Organize by app and feature (e.g., `core/run_create/partials/`)
- **JavaScript**: Modular by functionality with clear separation
- **Python**: Separate services, models, views, and utilities
- **Static Files**: Organize by type and usage context

### Frontend Consistency Requirements
- **Alpine.js Usage**: Use for reactive components, keep components small
- **Django Templates**: Follow standard inheritance and block patterns
- **Progressive Enhancement**: Ensure functionality works without JavaScript
- **Template Logic**: Keep business logic in Python, presentation in templates