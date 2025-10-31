# MVP Plan

## Goals
- Deliver a polished Micro SaaS web application for social media data extraction.
- Implement unified agent architecture for scraping, LLM processing, and validation.
- Support Instagram and TikTok platforms with flexible entity extraction.
- Provide professional UI with curation and export capabilities.
- Establish foundation for agentic features and MCP integration.

## Architecture Overview
- **Unified Agent**: Single agent handles Apify scraping + LLM entity extraction + validation + context-aware output formatting.
- **Web UI**: Generic entity list views with polished Micro SaaS styling (Material Design/shadcn).
- **MCP Server**: Returns data in multiple formats (file/markdown/JSON/CSV message).
- **Data Model**: Flexible JSONB-based entities supporting various extraction schemas.

## Implementation Phases

### Phase 1: Core Infrastructure
1. Complete Supabase integration (auth, database migration).
2. Set up production Docker configuration.
3. Implement basic agent framework in n8n.

### Phase 2: Agent & Processing
1. Build unified agent for scraping + LLM extraction + validation.
2. Add TikTok platform support.
3. Implement entity validation modules.

### Phase 3: User Interface
1. Create generic entity list views.
2. Implement polished Micro SaaS styling (Material/shadcn).
3. Build curation interface (add/edit notes, categories, collections).

### Phase 4: Business Features
1. Add CSV/JSON export functionality.
2. Integrate Stripe test payments.
3. Implement usage-based pricing display.

### Phase 5: MCP Foundation
1. Build MCP server with multiple output formats.
2. Test agent responses for different contexts.
3. Document MCP integration patterns.

## Success Criteria
- Professional web application with polished UI/UX.
- Reliable agent-based data extraction from Instagram/TikTok.
- Flexible entity curation and export capabilities.
- Foundation for advanced agentic features.
- Deployable MVP ready for user testing.

## Testing Strategy
- End-to-end agent workflows (scraping → extraction → validation).
- UI/UX testing with focus on professional appearance.
- MCP server integration testing.
- Multi-platform scraping verification.
- Export functionality validation.

## Deployment
- Containerized with Docker.
- Ready for Render deployment.
- Environment-specific configurations.