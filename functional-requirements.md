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

### Recommendation Scraping & Processing
- **As a user**, I want to trigger scraping of specified profiles so that location data is extracted from posts.
- **As a user**, I want the system to automatically extract locations, geocode them, and categorize recommendations so that I don't have to do manual work.

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
- API endpoints for triggering n8n workflows.
- Views for CRUD operations on lists/locations.
- Stripe webhook handlers for subscription events.

### External Integrations
- Supabase: Auth, DB, Analytics.
- n8n: Workflow orchestration for scraping/processing.
- Apify: Scraping actors (called via n8n).
- Stripe: Payment processing.
- Google Maps: Geocoding API, My Maps export.

## Acceptance Criteria
- All user stories must have corresponding UI/API implementations.
- Data must be securely stored and tied to user accounts.
- Exports must be compatible with Google My Maps.
- Subscriptions must enforce feature limits (e.g., free tier restrictions).