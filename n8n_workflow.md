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

Access n8n at http://localhost:5678 (user: user, password: password)