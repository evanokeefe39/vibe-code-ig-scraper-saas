# Functional Requirements

## Overview
The Vibe Code IG Scraper SaaS allows users to curate location-based recommendations from social media profiles into personalized lists for easy access on Google Maps.

## User Stories

### User Authentication & Management
- **As a user**, I want to sign up/login with Google or Apple so that I can access my personalized account.
- **As a user**, I want to manage my profile so that I can update my preferences and view my subscription status.

### Social Media Profile Management
- **As a user**, I want to add public social media profiles (e.g., Instagram, TikTok) so that I can specify sources for recommendations.
- **As a user**, I want to view and edit my added profiles so that I can keep them up-to-date.
- **As a user**, I want agents to dynamically select optimal scraping tools based on profile type and cost.

### Recommendation Scraping & Processing
- **As a user**, I want to trigger scraping of specified profiles so that location data is extracted from posts.
- **As a user**, I want the system to automatically extract locations, geocode them, and categorize recommendations so that I don't have to do manual work.
- **As a user**, I want to provide custom system prompts for data extraction so that I can tailor scraping behavior.
- **As a user**, I want agents to validate and sanitize my prompts to prevent malicious use.

### Curation & Organization
- **As a user**, I want to review extracted locations so that I can add notes, descriptions, and categories.
- **As a user**, I want to create and manage multiple curated lists so that I can organize recommendations by theme (e.g., cafes, bars).
- **As a user**, I want to edit or delete locations/lists so that I can maintain accurate data.

### Export & Integration
- **As a user**, I want to export curated lists to Google My Maps so that I can view locations on Google Maps.
- **As a user**, I want to download lists in formats like KML/CSV so that I can use them in other mapping tools.

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
- Profile and Location models.
- API endpoints for triggering n8n workflows and agent orchestration.
- Views for CRUD operations on lists/locations.
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
- **Scraping Trigger Endpoint**: POST /api/scrape/ - accepts profile URLs, validates user tier, constructs n8n payload, triggers workflow or agent.
- **Curation Workflow Endpoint**: POST /api/curate/ - accepts user preferences for sorting/filtering, triggers n8n curation workflow.
- **Location Management**: CRUD endpoints for viewing/editing scraped locations.
- **Export Endpoint**: GET /api/export/ - generates Google My Maps compatible files based on curated lists.
- **Prompt Management**: Endpoints for submitting and validating custom system prompts.

## Acceptance Criteria
- All user stories must have corresponding UI/API implementations.
- Data must be securely stored and tied to user accounts.
- Geocoding must achieve >90% accuracy for well-formed location strings, with fallback handling for partial matches.
- Exports must be compatible with Google My Maps.
- Subscriptions must enforce feature limits with dynamic cost estimation.
- URL validation prevents SSRF and malicious scraping.
- All API endpoints require authentication and respect user tiers.
- Curation workflows allow flexible sorting (by category, rating, location type).
- User prompts are sanitized to prevent malicious use.
- Agents can dynamically select tools based on cost and effectiveness.
- Complex data types are validated using specialized modules.