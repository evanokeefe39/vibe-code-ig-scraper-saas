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
- Implement unified agent for web UI and MCP server.
- Generic entity list views in Django with CSV/JSON export.
- MCP server with multiple output formats (file/markdown/JSON/CSV message).
- Subscription enforcement with dynamic pricing based on API usage.
- Set up CI/CD and monitoring.
- Implement user-provided system prompts for LLM entity extraction with sanitization.
- Agent uses Apify for scraping + LLM for entity extraction + validation.
- Research and implement cost querying for Apify actors (or hardcode estimates with user confirmation).
**Deliverables**: Public beta launch with unified agent handling both web UI and MCP requests.

## Stage 5: Second Release (Full Agentic Platform)
**Milestones**:
- Expand to multi-platform scraping (TikTok, etc.) via agent-driven decisions.
- Improve entity extraction with advanced LLM models and validation.
- User analytics dashboard with cost insights.
- Enhanced MCP server capabilities.
- Performance optimizations and advanced entity validation modules.
- Migrate to LangChain for sophisticated agent capabilities.
- Develop specialized validators for complex entity types.
**Deliverables**: Polished v1.0 release as unified agentic data extraction platform.

## Post-Release (Ongoing)
- Bug fixes and user feedback.
- Feature additions based on metrics.
- Scale to 1000+ users.
- Explore partnerships/monetization tweaks.

## Agentic Vision & TODOs
- **Unified Agent**: Single agent handles web UI and MCP server requests - scrapes with Apify, extracts entities with LLM, validates data, formats output appropriately.
- **Dynamic Pipelines**: Agents decide when/how to call Apify actors based on cost, success rates, and user goals for various data extraction tasks.
- **Cost Management**: Query Apify actor costs via API (research needed); fallback to hardcoded estimates with user confirmation dialogs.
- **Prompt Sanitization**: Implement input validation for user prompts using frameworks like Guardrails AI or NeMo Guardrails to detect malicious content.
- **Entity Validation**: Develop validation for extracted entities (location geocoding, contact info, etc.).
- **MCP Integration**: Expose agent as MCP server that returns data in multiple formats (file/markdown/JSON/CSV message).
- **Generic Entity Views**: Django UI shows flexible list of extracted entities with CSV/JSON export.
- **Project Rename**: Consider renaming from "IG Scraper SaaS" to "Agentic Social Scraper" or similar to reflect expanded scope.
- **Agent Framework**: Start with n8n for agentic workflows, transition to LangChain for maturity.

## Risks & Dependencies
- Apify API limits/costs.
- Supabase reliability.
- Stripe integration complexity.
- User acquisition for validation.