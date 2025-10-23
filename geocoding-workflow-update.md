# Geocoding Workflow Update Guide

This guide provides step-by-step instructions to update the n8n workflow from Nominatim to Mapbox geocoding.

## Background

The current workflow uses Nominatim (OpenStreetMap) for geocoding, but we've switched to Mapbox for better accuracy, fuzzy matching, and reliability. This update requires modifying the "Geocode" HTTP Request node.

## Prerequisites

1. Mapbox account and access token (see `geocoding-setup.md`)
2. n8n workflow editor access
3. The workflow file: `n8n/workflows/Scrape Instagram and Process Locations.json`

## Step-by-Step Update Instructions

### 1. Open the Workflow in n8n

1. Import or open the workflow "Scrape Instagram and Process Locations"
2. Locate the "Geocode" node (currently disabled, using Nominatim)

### 2. Update the HTTP Request Node

#### Current Configuration (Nominatim):
- **Method**: GET
- **URL**: `https://nominatim.openstreetmap.org/search`
- **Query Parameters**: (address passed in URL or body)

#### New Configuration (Mapbox):

1. **Method**: Keep as GET

2. **URL**: Change to:
   ```
   https://api.mapbox.com/geocoding/v5/mapbox.places/{{ encodeURIComponent($json.address) }}.json
   ```

3. **Query Parameters**:
   - **access_token**: `{{$credentials.mapboxToken}}` (or however you store the token)
   - **fuzzyMatch**: `true`

4. **Authentication**:
   - If using credential: Select "Mapbox API Token" credential
   - Or add header: `Authorization: Bearer YOUR_TOKEN`

### 3. Update Data Processing

The Mapbox API returns data in a different format than Nominatim. Update any downstream nodes that process geocoding results.

#### Nominatim Response Format:
```json
[
  {
    "lat": "48.8566",
    "lon": "2.3522",
    "display_name": "Paris, France"
  }
]
```

#### Mapbox Response Format:
```json
{
  "features": [
    {
      "center": [2.3522, 48.8566],
      "place_name": "Paris, Île-de-France, France",
      "context": [...]
    }
  ]
}
```

### 4. Update Data Mapping

If you have nodes that extract latitude/longitude, update them:

**Before (Nominatim)**:
- Latitude: `{{ $json[0].lat }}`
- Longitude: `{{ $json[0].lon }}`

**After (Mapbox)**:
- Latitude: `{{ $json.features[0].center[1] }}`
- Longitude: `{{ $json.features[0].center[0] }}`

### 5. Enable the Node

1. Uncheck "Disabled" on the Geocode node
2. Ensure it's properly connected in the workflow

### 6. Test the Updated Workflow

1. Use test data with known addresses
2. Verify coordinates are correct
3. Check error handling for failed geocoding

## Sample Test Addresses

Test with these addresses to verify fuzzy matching:

- "4 rue de la Convention, 75015 Paris" (exact address)
- "rue de la Convention Paris" (partial)
- "Convention Paris 15" (very partial)
- "4 rue Convention 75015" (typo/missing words)

Expected results should include accurate coordinates for Paris 15th arrondissement.

## Error Handling

Add error handling for cases where geocoding fails:

1. Check if `features` array is empty
2. Log failed addresses for manual review
3. Continue workflow without coordinates rather than failing

## Performance Considerations

- Mapbox has rate limits (100k free requests/month)
- Enable fuzzy matching for better success rates
- Consider caching successful geocoding results

## Rollback Plan

If issues arise:
1. Disable the Mapbox Geocode node
2. Re-enable any backup geocoding logic
3. Monitor and fix issues before re-enabling

## Validation Checklist

- [ ] Mapbox credential configured in n8n
- [ ] HTTP Request URL updated to Mapbox endpoint
- [ ] Query parameters include access_token and fuzzyMatch=true
- [ ] Downstream nodes updated to handle Mapbox response format
- [ ] Node enabled in workflow
- [ ] Test with sample addresses successful
- [ ] Error handling implemented
- [ ] Documentation updated

## Related Files

- `geocoding-setup.md`: API setup instructions
- `n8n/README.md`: Workflow overview
- `geocoding-providers.md`: Provider comparison details