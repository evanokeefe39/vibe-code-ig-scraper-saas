# Roadmap

## Overview
Phased development from boilerplate to full product release, with milestones and timelines.

## Stage 1: Init & Boilerplate (Week 1-2)
**Milestones**:
- Set up Poetry, Django project.
- Create basic apps: users, core.
- Implement user auth stubs.
- Write initial tests and docs.
**Deliverables**: Functional local dev environment.
**Timeline**: 2 weeks.

## Stage 2: Proof of Concept (Week 3-4)
**Milestones**:
- Integrate n8n with Apify.
- Build scraping workflow (Instagram).
- Add geocoding and basic processing.
- Test end-to-end flow.
**Deliverables**: Working scrape-to-store pipeline.
**Timeline**: 2 weeks.

## Stage 3: Minimum Viable Product (Week 5-8)
**Milestones**:
- Full Supabase integration.
- Develop curation UI.
- Implement basic export (CSV).
- Add Stripe test payments.
- Containerize with Docker.
**Deliverables**: Deployable MVP for internal use.
**Timeline**: 4 weeks.

## Stage 4: First Release (Week 9-12)
**Milestones**:
- Deploy to Render production.
- Enhance UI/UX.
- Full Google My Maps export.
- Subscription enforcement.
- Set up CI/CD and monitoring.
**Deliverables**: Public beta launch.
**Timeline**: 4 weeks.

## Stage 5: Second Release (Week 13-16)
**Milestones**:
- Add TikTok scraping.
- Improve NLP categorization.
- User analytics dashboard.
- API for integrations.
- Performance optimizations.
**Deliverables**: Polished v1.0 release.
**Timeline**: 4 weeks.

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