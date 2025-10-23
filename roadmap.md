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

## Stage 2: Proof of Concept ✅ COMPLETED
**Milestones**:
- Integrate n8n with Apify.
- Build scraping workflow (Instagram).
- Add Mapbox geocoding and basic processing.
- Test end-to-end flow.
**Deliverables**: Working scrape-to-store pipeline.
**Completed**: End-to-end Django → n8n → Postgres pipeline validated. Data stored as JSONB in core_run.output. n8n_execution_id used for correlation.

## Stage 3: Minimum Viable Product
**Milestones**:
- Full Supabase integration.
- Develop curation UI.
- Implement basic export (CSV).
- Add Stripe test payments.
- Containerize with Docker.
- Add TikTok as second social media profile option.
**Deliverables**: Deployable MVP for internal use with web GUI focused on location data but extensible to other use cases.
**Future Agentic Prep**: Design n8n pipelines to be modular (split scraping and data validation) for eventual conversion to agent tools.

## Stage 4: First Release (Agentic Foundations)
**Milestones**:
- Deploy to Render production.
- Enhance UI/UX for multiple data types.
- Full export to Google My Maps (for location data) and flexible formats.
- Subscription enforcement with dynamic pricing based on API usage.
- Set up CI/CD and monitoring.
- Implement user-provided system prompts for data extraction with sanitization.
- Wrap n8n pipelines as agent tools; introduce basic agent orchestration using n8n components.
- Research and implement cost querying for Apify actors (or hardcode estimates with user confirmation).
**Deliverables**: Public beta launch with agentic scraping capabilities adaptable to various use cases.

## Stage 5: Second Release (Full Agentic Platform)
**Milestones**:
- Expand to multi-platform scraping (TikTok, etc.) via agent-driven decisions.
- Improve NLP categorization with agent-selected models for various data types.
- User analytics dashboard with cost insights.
- API for integrations and MCP client/server exposure.
- Performance optimizations and dynamic data validation modules for extensible schemas.
- Migrate to LangChain for advanced agent capabilities.
- Develop specialized validators for complex types (JSON, currency, timestamps, custom schemas).
**Deliverables**: Polished v1.0 release as flexible agentic data extraction platform.

## Post-Release (Ongoing)
- Bug fixes and user feedback.
- Feature additions based on metrics.
- Scale to 1000+ users.
- Explore partnerships/monetization tweaks.

## Agentic Vision & TODOs
- **Dynamic Pipelines**: Agents decide when/how to call Apify actors based on cost, success rates, and user goals for various data extraction tasks.
- **Cost Management**: Query Apify actor costs via API (research needed); fallback to hardcoded estimates with user confirmation dialogs.
- **Prompt Sanitization**: Implement input validation for user prompts using frameworks like Guardrails AI or NeMo Guardrails to detect malicious content.
- **Data Validation Modules**: Develop reusable tools for complex types (JSON schema, currency parsing, timestamp validation, location geocoding, custom user-defined schemas).
- **MCP Integration**: Expose scraping tools as MCP servers for broader AI agent ecosystems.
- **Project Rename**: Consider renaming from "IG Scraper SaaS" to "Agentic Social Scraper" or similar to reflect expanded scope.
- **Agent Framework**: Start with n8n for agentic workflows, transition to LangChain for maturity.
- **Schema Flexibility**: Support user-defined data extraction schemas beyond hardcoded location processing.

## Risks & Dependencies
- Apify API limits/costs.
- Supabase reliability.
- Stripe integration complexity.
- User acquisition for validation.