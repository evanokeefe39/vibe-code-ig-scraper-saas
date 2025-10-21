# Roadmap

## Overview
Phased development from boilerplate to full product release, with milestones and timelines.

## Stage 1: Init & Boilerplate
**Milestones**:
- Set up Poetry, Django project.
- Create basic apps: users, core.
- Implement user auth stubs.
- Write initial tests and docs.
**Deliverables**: Functional local dev environment.

## Stage 2: Proof of Concept
**Milestones**:
- Integrate n8n with Apify.
- Build scraping workflow (Instagram).
- Add geocoding and basic processing.
- Test end-to-end flow.
**Deliverables**: Working scrape-to-store pipeline.

## Stage 3: Minimum Viable Product
**Milestones**:
- Full Supabase integration.
- Develop curation UI.
- Implement basic export (CSV).
- Add Stripe test payments.
- Containerize with Docker.
**Deliverables**: Deployable MVP for internal use.

## Stage 4: First Release
**Milestones**:
- Deploy to Render production.
- Enhance UI/UX.
- Full Google My Maps export.
- Subscription enforcement.
- Set up CI/CD and monitoring.
**Deliverables**: Public beta launch.

## Stage 5: Second Release
**Milestones**:
- Add TikTok scraping.
- Improve NLP categorization.
- User analytics dashboard.
- API for integrations.
- Performance optimizations.
**Deliverables**: Polished v1.0 release.

## Post-Release (Ongoing)
- Bug fixes and user feedback.
- Feature additions based on metrics.
- Scale to 1000+ users.
- Explore partnerships/monetization tweaks.

## Risks & Dependencies
- Apify API limits/costs.
- Supabase reliability.
- Stripe integration complexity.
- User acquisition for validation.