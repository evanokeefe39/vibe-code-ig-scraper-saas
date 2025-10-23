# High-Level Architecture

## Overall System Architecture

### Core Components
- **Frontend**: Django templates for web UI.
- **Backend**: Django server for API, auth, and business logic.
- **Database**: Supabase (Postgres) for data storage.
- **Orchestration**: n8n for async workflows (scraping, processing).
- **Integrations**: Apify (scraping), Stripe (payments), Mapbox (geocoding), Google Maps (export).
- **Hosting**: Render (containerized deployment).
- **DevOps**: GitHub (version control, CI/CD, issues).

### Geocoding Service

The geocoding service converts location strings from scraped Instagram data into latitude/longitude coordinates for mapping.

**Flow**:
1. Scraper extracts location strings (e.g., "4 rue de la Convention, 75015 Paris").
2. n8n workflow sends location to Mapbox Geocoding API.
3. API returns coordinates with confidence score.
4. Coordinates stored in Supabase with location metadata.

**Constraints**:
- Primary provider: Mapbox (excellent fuzzy matching, 100k free req/month).
- Fallback: Nominatim (free, no API key, but lower accuracy).
- Rate limits: Respect API quotas; implement caching and retry logic.
- Accuracy: Target >90% success rate for well-formed addresses.
- Privacy: No user data sent to geocoding providers.

See [geocoding-providers.md](geocoding-providers.md) for provider details.

### Data Flow
1. User → Django (auth/UI) → n8n (trigger scrape) → Apify (scrape) → n8n (process) → Supabase (store).
2. User → Django (curation) → Supabase (CRUD) → Export (Google Maps).
3. Payments: Stripe buy buttons → Webhooks → Supabase.

## Architecture by Stage

### Stage 1: Init & Boilerplate
**Goal**: Set up project foundation.
**Architecture**:
- Local dev: Poetry + Django + basic models.
- No external integrations yet.
- Simple Django app with auth stubs.
- Files: `pyproject.toml`, `manage.py`, basic apps (users, core).

### Stage 2: Proof of Concept (POC)
**Goal**: Validate core scraping and processing.
**Architecture**:
- Add n8n locally (docker-compose).
- Integrate Apify in n8n workflows.
- Basic geocoding (Mapbox).
- Django API to trigger n8n.
- Supabase for DB (local mock if needed).
- Test end-to-end: Scrape → Process → Store.

### Stage 3: Minimum Viable Product (MVP)
**Goal**: Functional app for internal testing.
**Architecture**:
- Full Supabase integration (auth, DB).
- Curation UI in Django templates.
- Basic export (CSV).
- Stripe buy buttons (test mode).
- Metrics with Supabase Analytics.
- Containerized with Docker.
- Deploy to Render (staging).

### Stage 4: First Release
**Goal**: Public beta with core features.
**Architecture**:
- Production Supabase/Render.
- Enhanced UI (responsive design).
- Full export to Google My Maps.
- Subscription enforcement.
- Error handling and logging.
- CI/CD with GitHub Actions.
- Monitoring and alerts.

### Stage 5: Second Release
**Goal**: Polished product with advanced features.
**Architecture**:
- Multi-platform scraping (TikTok, etc.).
- Advanced NLP for better categorization.
- User analytics dashboard.
- API for third-party integrations.
- Scalability optimizations (caching, CDN).
- Internationalization.
- Enterprise features (team accounts).