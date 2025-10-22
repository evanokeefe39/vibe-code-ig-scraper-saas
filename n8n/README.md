# n8n Workflows Documentation

This directory contains n8n workflows for the Instagram scraper SaaS application.

## Overview

The workflows automate the process of:
1. Scraping Instagram posts from specified profiles
2. Extracting location information from captions using LLM
3. Geocoding addresses to coordinates
4. Storing processed data in Supabase

## Workflows

### Scrape Instagram and Process Locations

**File**: `workflows/Scrape Instagram and Process Locations.json`

**Purpose**: Main workflow that orchestrates the entire scraping and processing pipeline.

**Nodes**:
- **Webhook**: Receives scraping requests with profile URLs and parameters
- **Run an Actor and get dataset**: Uses Apify Instagram Scraper to fetch posts
- **Basic LLM Chain**: Processes captions with Grok to extract business names, addresses, categories, vibes, and cost notes
- **Code in JavaScript**: Parses and validates LLM JSON output
- **Extract Locations** (disabled): Legacy regex-based location extraction
- **Geocode** (disabled): Legacy Nominatim geocoding
- **Supabase**: Stores processed location data

**Input Format**:
```json
{
  "user_id": 1,
  "tier": "premium",
  "profiles": [
    {
      "url": "https://www.instagram.com/username/",
      "days_since": 30,
      "type": "instagram",
      "max_results": 50
    }
  ]
}
```

**Output**: Processed location data stored in Supabase with coordinates, categories, and metadata.

## Workflow Updates

### Switching from Nominatim to Mapbox Geocoding

Due to accuracy and reliability improvements, the geocoding has been switched from Nominatim to Mapbox.

**Changes Required**:
1. Update the "Geocode" HTTP Request node to use Mapbox API
2. Add Mapbox access token credential
3. Enable fuzzy matching for better address handling

**Detailed Instructions**: See `../geocoding-workflow-update.md`

## Setup Requirements

1. **Apify Account**: For Instagram scraping
   - Create account at apify.com
   - Get API token
   - Add to n8n credentials as "Apify account"

2. **OpenRouter Account**: For LLM processing
   - Create account at openrouter.ai
   - Get API key
   - Add to n8n credentials as "OpenRouter account"

3. **Mapbox Account**: For geocoding
   - Create account at mapbox.com
   - Get access token
   - Add to n8n credentials as "Mapbox API Token"

4. **Supabase Account**: For data storage
   - Set up Supabase project
   - Get connection details
   - Add to n8n credentials as Supabase connection

## Running Workflows

1. Import the workflow JSON into n8n
2. Set up all required credentials
3. Activate the workflow
4. Send POST requests to the webhook endpoint with profile data

## Monitoring and Debugging

- Check n8n execution logs for errors
- Monitor API usage in respective dashboards (Apify, Mapbox, OpenRouter)
- Use n8n's built-in testing features for individual nodes

## Performance Considerations

- Instagram scraping can be rate-limited; respect API limits
- LLM processing is the most expensive step; optimize prompts
- Geocoding requests should be batched when possible
- Monitor Supabase usage for database costs

## Security Notes

- Never commit API keys to version control
- Use n8n's credential management for all secrets
- Regularly rotate API tokens
- Monitor for unusual API usage patterns

## Troubleshooting

**Common Issues**:
- **Instagram scraping fails**: Check Apify actor status and input parameters
- **LLM parsing errors**: Review prompt and JSON parsing logic
- **Geocoding failures**: Verify Mapbox token and address formats
- **Supabase connection issues**: Check credentials and network connectivity

**Logs Location**: Check n8n workflow execution history for detailed error messages.

## Development

When modifying workflows:
- Test changes in a development environment first
- Document any new nodes or logic changes
- Update this README with new setup requirements
- Version control workflow JSON files appropriately

## Related Documentation

- `../geocoding-setup.md`: Mapbox API setup guide
- `../geocoding-workflow-update.md`: Step-by-step workflow update instructions
- `../architecture.md`: System architecture overview
- `../functional-requirements.md`: Feature requirements

## Legacy Information

### Input for Scraper (Apify Actor)

```json
{
  "addParentData": false,
  "directUrls": [
    "https://www.instagram.com/ellevousguide/"
  ],
  "enhanceUserSearchWithFacebookPage": false,
  "isUserReelFeedURL": false,
  "isUserTaggedFeedURL": false,
  "onlyPostsNewerThan": "10 days",
  "resultsLimit": 1,
  "resultsType": "posts",
  "searchLimit": 1,
  "searchType": "hashtag"
}
```

### Test URL for Workflow
http://localhost:5678/webhook-test/scrape

### Test Profiles
- https://www.instagram.com/parisfoodguide_/
- https://www.instagram.com/ellevousguide/
- https://www.instagram.com/_lavieparisienne__/
- https://www.instagram.com/le__walk/
- https://www.instagram.com/sagevanalstine/
- https://www.instagram.com/paname_in_my_belly/