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
- **As a user**, I want to trigger scraping of specified profiles so that structured data is extracted from posts.
- **As a user**, I want the system to automatically extract and process data according to my specifications (e.g., locations with geocoding, leads with contact info, etc.) so that I don't have to do manual work.
- **As a user**, I want to provide custom system prompts for data extraction so that I can tailor scraping behavior to different use cases.
- **As a user**, I want agents to validate and sanitize my prompts to prevent malicious use.

### Curation & Organization
- **As a user**, I want to review extracted data so that I can add notes, descriptions, and categories.
- **As a user**, I want to create and manage multiple curated collections so that I can organize data by theme or purpose (e.g., travel spots, business leads).
- **As a user**, I want to edit or delete data/collections so that I can maintain accurate information.

### Export & Integration
- **As a user**, I want to export curated collections in various formats (CSV, JSON, Google My Maps for location data) so that I can use them in other tools and applications.
- **As a user**, I want flexible export options that adapt to the type of data collected.

### Payments & Subscriptions
- **As a user**, I want to view available subscription plans so that I can choose the right tier.
- **As a user**, I want to subscribe via Stripe checkout so that I can access premium features.
- **As a user**, I want to manage my subscription (upgrade/downgrade/cancel) so that I can control my billing.
- **As a user**, I want to see cost estimates for scraping operations before confirming so that I can manage expenses.
- **As a user**, I want dynamic pricing based on actual API usage and agent decisions.

### Metrics & Analytics (Admin/Internal)
- **As an admin**, I want to track user metrics (signups, usage, conversions) so that I can monitor business health.
- **As an admin**, I want to monitor system performance and costs so that I can optimize operations.

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
- Profile and flexible data models (JSONB-based for adaptability).
- API endpoints for triggering n8n workflows and agent orchestration.
- Views for CRUD operations on collections and extracted data.
- Stripe webhook handlers for subscription events with usage tracking.
- Prompt sanitization and validation for user inputs.

### External Integrations
- Supabase: Auth, DB, Analytics.
- n8n: Workflow orchestration and initial agent tools.
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
- **Scraping Trigger Endpoint**: POST /api/scrape/ - accepts profile URLs and extraction specifications, validates user tier, constructs n8n payload, triggers workflow or agent.
- **Curation Workflow Endpoint**: POST /api/curate/ - accepts user preferences for sorting/filtering, triggers n8n curation workflow.
- **Data Management**: CRUD endpoints for viewing/editing scraped data with flexible schemas.
- **Export Endpoint**: GET /api/export/ - generates files in requested formats based on curated collections.
- **Prompt Management**: Endpoints for submitting and validating custom system prompts.

## Acceptance Criteria
- All user stories must have corresponding UI/API implementations.
- Data must be securely stored and tied to user accounts.
- For location data: Geocoding must achieve >90% accuracy for well-formed location strings, with fallback handling for partial matches.
- Exports must be compatible with target formats (Google My Maps for location data, CSV/JSON for general data).
- Subscriptions must enforce feature limits with dynamic cost estimation.
- URL validation prevents SSRF and malicious scraping.
- All API endpoints require authentication and respect user tiers.
- Curation workflows allow flexible sorting and filtering based on extracted data types.
- User prompts are sanitized to prevent malicious use.
- Agents can dynamically select tools based on cost and effectiveness.
- Complex data types are validated using specialized modules.
- The system must be adaptable to different data extraction schemas beyond locations.