# High-Level Architecture

## Overall System Architecture

### Core Components
- **Frontend**: Django templates for web UI.
- **Backend**: Django server for API, auth, and business logic.
- **Database**: Supabase (Postgres) for data storage with JSONB flexibility.
- **Orchestration**: n8n for async workflows (scraping, processing) with modular design for agent conversion.
- **Integrations**: Apify (scraping), Stripe (payments), Mapbox (geocoding for location data), Google Maps (export for location data).
- **Hosting**: Render (containerized deployment).
- **DevOps**: GitHub (version control, CI/CD, issues).

### Data Processing Services

The platform supports various data processing services depending on the extraction use case. For location data (current focus):

**Geocoding Service Flow**:
1. Scraper extracts location strings (e.g., "4 rue de la Convention, 75015 Paris").
2. n8n workflow sends location to Mapbox Geocoding API.
3. API returns coordinates with confidence score.
4. Coordinates stored in Supabase with location metadata.

**Extensible Processing**:
- The system is designed to support additional processing services (e.g., entity extraction, sentiment analysis, data validation) based on user requirements.
- Processing modules can be added as n8n nodes or agent tools.

**Constraints**:
- Primary provider: Mapbox (excellent fuzzy matching, 100k free req/month).
- Fallback: Nominatim (free, no API key, but lower accuracy).
- Rate limits: Respect API quotas; implement caching and retry logic.
- Accuracy: Target >90% success rate for well-formed addresses.
- Privacy: No user data sent to external processing providers.

See [geocoding-providers.md](geocoding-providers.md) for provider details.

### Data Flow
1. **Web UI Flow**: User → Django (auth/UI) → Agent (scrape via Apify + LLM extraction + validation) → Django DB (store entities as flexible JSONB) → Generic entity list view → Export (CSV/JSON).
2. **MCP Flow**: External agent → MCP server → Internal agent (scrape + extraction + validation) → Return data (file/markdown/JSON/CSV message).
3. Payments: Stripe buy buttons → Webhooks → DB.

**Unified Agent Architecture**: A single agent handles both web UI and MCP requests. The agent:
- Scrapes social media profiles using Apify
- Uses LLM to extract entities based on user prompts
- Validates extracted entities
- Formats output based on context (DB storage for web UI, direct response for MCP)

**Data Storage Decision**: Extracted entities stored as JSONB structures in Django models for maximum flexibility across different use cases (locations, leads, research data, etc.). n8n execution data remains in n8n; correlated via execution ID.

## Architecture by Stage

### Stage 1: Init & Boilerplate
**Goal**: Set up project foundation.
**Architecture**:
- Local dev: Poetry + Django + basic models.
- No external integrations yet.
- Simple Django app with auth stubs.
- Files: `pyproject.toml`, `manage.py`, basic apps (users, core).

### Stage 2: Proof of Concept (POC) ✅ COMPLETED
**Goal**: Validate core scraping and processing.
**Architecture**:
- Add n8n locally (docker-compose).
- Integrate Apify in n8n workflows.
- Basic geocoding (Mapbox).
- Django API to trigger n8n.
- PostgreSQL in Docker for DB (production-like environment).
- Data correlation: Django 'runs' linked to n8n executions via `n8n_execution_id`; no data replication to maintain separation of concerns.
- Location data stored as JSONB arrays in `core_run.output` for flexibility.
- Test end-to-end: Scrape → Process → Store.

### Stage 3: Minimum Viable Product (MVP)
**Goal**: Functional app for internal testing.
**Architecture**:
- Full Supabase integration (auth, DB).
- Curation UI in Django templates.
- Basic export (CSV).
- Stripe buy buttons (test mode) with dynamic pricing previews.
- Metrics with Supabase Analytics.
- Containerized with Docker.
- Deploy to Render (staging).
- Modular n8n pipelines (scraping + validation) prepared for agent tool conversion.

### Stage 4: First Release (Agentic Foundations)
**Goal**: Public beta with agentic scraping.
**Architecture**:
- Production Supabase/Render.
- Enhanced UI/UX with prompt customization.
- Full export to Google My Maps.
- Subscription enforcement with usage-based billing.
- Error handling and logging.
- CI/CD with GitHub Actions.
- Monitoring and alerts.
- Agent orchestration via n8n tools; basic cost estimation and user confirmation.

### Stage 5: Second Release (Full Agentic Platform)
**Goal**: Polished agentic scraping platform.
**Architecture**:
- Multi-platform scraping via agent decisions (TikTok, etc.).
- Advanced NLP with agent-selected models.
- User analytics dashboard with cost insights.
- API and MCP client/server for integrations.
- Scalability optimizations (caching, CDN).
- Internationalization.
- Enterprise features (team accounts).
- LangChain-based agents with specialized data validators.