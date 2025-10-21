# n8n Workflow for POC

## Workflow: Scrape Instagram and Process

1. **Webhook Trigger**: Receives profile URL from Django.
2. **Apify Instagram Scraper**: Scrapes posts from the profile.
3. **Data Processing**: Extract location mentions (e.g., via regex or NLP).
4. **Geocode**: Call geocoding API (or send to Django).
5. **Store**: Send processed data to Supabase or Django API.

## Nodes:
- Webhook
- Apify: Instagram Posts Scraper
- Function: Extract locations
- HTTP Request: Geocode via Nominatim
- Supabase: Insert data

## Import Workflow
The workflow is defined in `n8n/workflows/scrape-workflow.json`. To import:
1. Access n8n at http://localhost:5678 (user: user, password: password)
2. Go to Workflows > Import from File
3. Upload `scrape-workflow.json`
4. Configure credentials for Apify and Supabase.

Access n8n at http://localhost:5678 (user: user, password: password)