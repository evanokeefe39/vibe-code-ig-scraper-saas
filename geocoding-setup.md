# Geocoding Setup Guide

This guide explains how to set up geocoding for the Instagram scraper SaaS using Mapbox Geocoding API.

## Overview

The application uses geocoding to convert location addresses extracted from Instagram captions into latitude/longitude coordinates for mapping and location-based features.

## Mapbox Geocoding API

We use Mapbox Geocoding API as our primary geocoding provider due to its:
- High accuracy for global addresses
- Support for fuzzy matching (handles typos and incomplete addresses)
- Good coverage for international locations
- Reasonable pricing (free tier available)

### Getting a Mapbox Access Token

1. Go to [mapbox.com](https://account.mapbox.com/)
2. Sign up for a free account (or log in if you have one)
3. Navigate to the [Access Tokens](https://account.mapbox.com/access-tokens/) page
4. Create a new token or use the default one
5. Copy the token (starts with `pk.` for public tokens)

### Setting up in n8n

1. Open your n8n instance
2. Go to Settings > Credentials
3. Create a new credential of type "HTTP Basic Auth" or "Header Auth"
4. For Header Auth:
   - Name: `Mapbox API Token`
   - Header Name: `Authorization`
   - Header Value: `Bearer YOUR_MAPBOX_TOKEN_HERE`
5. Save the credential

### API Usage

The Mapbox Geocoding API endpoint:
```
GET https://api.mapbox.com/geocoding/v5/mapbox.places/{search_text}.json?access_token={token}&fuzzyMatch=true
```

Parameters:
- `search_text`: The address to geocode (URL-encoded)
- `access_token`: Your Mapbox token
- `fuzzyMatch`: Set to `true` for better handling of typos and incomplete addresses

### Rate Limits and Pricing

- Free tier: 100,000 requests/month
- Paid plans start at $0.75 per 1,000 requests
- Monitor usage in your Mapbox dashboard

### Testing the API

You can test the API directly:

```bash
curl "https://api.mapbox.com/geocoding/v5/mapbox.places/4%20rue%20de%20la%20Convention%2C%2075015%20Paris.json?access_token=YOUR_TOKEN&fuzzyMatch=true"
```

Expected response includes:
- `features[0].center`: [longitude, latitude]
- `features[0].place_name`: Formatted address
- `features[0].context`: Administrative boundaries

### Fallback Strategy

If Mapbox fails, the system should gracefully handle errors and continue processing without coordinates rather than failing the entire workflow.

## Environment Variables

For local development, add to your `.env` file:
```
MAPBOX_ACCESS_TOKEN=your_token_here
```

## Troubleshooting

- **Invalid token**: Check that your token is correct and has geocoding permissions
- **Rate limit exceeded**: Upgrade your plan or implement request throttling
- **No results**: Try with `fuzzyMatch=true` or simplify the address
- **International addresses**: Mapbox handles most global addresses well, but test with your target regions