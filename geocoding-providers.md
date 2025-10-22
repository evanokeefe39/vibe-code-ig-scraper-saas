# Geocoding Providers

This document outlines the geocoding providers evaluated for the Vibe Code Instagram Scraper SaaS project, including their features, costs, and selection rationale.

## Provider Comparison

| Provider          | Cost          | API Key Required | Accuracy | Fuzzy Matching | Rate Limits | Notes |
|-------------------|---------------|------------------|----------|----------------|-------------|-------|
| Nominatim (OSM)  | Free         | No              | Medium  | Limited       | 1 req/sec  | Open-source, but may be slow and less reliable for high volume |
| OpenCage         | Paid ($0.005/req) | Yes            | High    | Good          | 2500 req/day free tier | Good balance, but higher cost than Mapbox |
| Google Geocoding | Paid ($0.005-0.01/req) | Yes            | Very High | Excellent     | 40,000 req/day free tier | Expensive for high volume, requires billing setup |
| Mapbox Geocoding | Paid ($0.0075/req) | Yes            | High    | Excellent     | 100,000 req/month free tier | Excellent fuzzy matching, good for maps integration, balanced cost |

## Selection Logic

For the POC/MVP phase:
- **Primary Choice: Mapbox** - Selected for its excellent fuzzy matching capabilities, reasonable cost, and integration with mapping features. The free tier (100,000 requests/month) is sufficient for initial testing and small-scale deployment.
- **Fallback: Nominatim** - Used as a free alternative if Mapbox quota is exceeded or for development/testing without API keys.
- **Future Consideration: OpenCage or Google** - If higher accuracy is needed or if Mapbox proves insufficient for specific use cases.

## Mapbox Setup

### Getting an API Key
1. Sign up for a Mapbox account at [mapbox.com](https://account.mapbox.com/).
2. Create a new token in the Account > Access Tokens section.
3. Copy the token (starts with `pk.` for public tokens or `sk.` for secret tokens).

### API Usage
- Endpoint: `https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json`
- Parameters:
  - `access_token`: Your API key
  - `limit`: Number of results (default 1)
  - `fuzzyMatch`: Enable fuzzy matching (default true)
  - `autocomplete`: Enable autocomplete (default true)
- Example: `https://api.mapbox.com/geocoding/v5/mapbox.places/4%20rue%20de%20la%20Convention%2C%2075015%20Paris.json?access_token=YOUR_TOKEN&fuzzyMatch=true`

### Integration Notes
- Store API key securely (environment variable: `MAPBOX_ACCESS_TOKEN`)
- Handle rate limits and errors gracefully
- Cache results to reduce API calls
- For production, monitor usage and costs

## Nominatim Setup (Fallback)

### API Usage
- Endpoint: `https://nominatim.openstreetmap.org/search`
- Parameters:
  - `q`: Query string
  - `format`: json
  - `limit`: 1
- Example: `https://nominatim.openstreetmap.org/search?q=4%20rue%20de%20la%20Convention%2C%2075015%20Paris&format=json&limit=1`
- No API key required, but include User-Agent header

### Limitations
- Rate limited (1 req/sec)
- Less accurate for partial or misspelled addresses
- No fuzzy matching built-in