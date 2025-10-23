# Geocoding Test Plan

This document outlines the testing strategy for the Mapbox geocoding integration.

## Test Objectives

- Verify Mapbox API integration works correctly
- Validate fuzzy matching handles various address formats
- Ensure error handling for failed geocoding
- Confirm coordinate accuracy

## Test Cases

### Sample Addresses

Test the following addresses extracted from Instagram captions:

1. **Exact Address**: "4 rue de la Convention, 75015 Paris"
   - Expected: Coordinates for 4 Rue de la Convention, Paris 15e
   - Approximate coordinates: [2.2833, 48.8417]

2. **Partial Address**: "rue de la Convention Paris"
   - Expected: Coordinates for Rue de la Convention area
   - Should fuzzy match to the street

3. **Minimal Info**: "Convention Paris 15"
   - Expected: Coordinates for Paris 15th arrondissement
   - Tests fuzzy matching with minimal context

4. **Typo/Abbreviated**: "4 rue Convention 75015"
   - Expected: Still resolves to correct location
   - Tests fuzzy matching tolerance

5. **Business with Address**: "Paris & Co 4 rue de la Convention, 75015 Paris"
   - Expected: Coordinates for the bakery location
   - Should extract and geocode the address portion

6. **Multiple Locations**: "49 rue de la Gaité, 75014 Paris" (from sample data)
   - Expected: Coordinates for Montparnasse area

### Test Procedure

1. **Manual API Testing**:
   ```bash
   # Test exact address
   curl "https://api.mapbox.com/geocoding/v5/mapbox.places/4%20rue%20de%20la%20Convention%2C%2075015%20Paris.json?access_token=YOUR_TOKEN&fuzzyMatch=true"

   # Test partial address
   curl "https://api.mapbox.com/geocoding/v5/mapbox.places/rue%20de%20la%20Convention%20Paris.json?access_token=YOUR_TOKEN&fuzzyMatch=true"
   ```

2. **Workflow Testing**:
   - Update workflow with Mapbox configuration
   - Run test executions with sample data
   - Verify coordinates in Supabase output

3. **Integration Testing**:
   - Test full workflow with real Instagram data
   - Verify geocoding results are stored correctly
   - Check for any failed geocoding attempts

## Expected Results

### Success Criteria

- **Accuracy**: Coordinates within 100m of actual location
- **Success Rate**: >90% for well-formed addresses
- **Fuzzy Matching**: >70% success for partial/incomplete addresses
- **Error Handling**: Failed geocoding doesn't break workflow

### Response Format Validation

Mapbox API response should include:
```json
{
  "features": [
    {
      "center": [longitude, latitude],
      "place_name": "formatted address",
      "relevance": 0.9,
      "context": [...]
    }
  ]
}
```

### Coordinate Extraction

In n8n workflow:
- Latitude: `{{ $json.features[0].center[1] }}`
- Longitude: `{{ $json.features[0].center[0] }}`
- Confidence: `{{ $json.features[0].relevance }}`

## Error Scenarios

### No Results
- API returns empty `features` array
- Should log warning and continue without coordinates

### API Errors
- Rate limit exceeded (HTTP 429)
- Invalid token (HTTP 401)
- Should retry or fallback gracefully

### Network Issues
- Timeout or connection failures
- Should have retry logic

## Performance Benchmarks

- **Response Time**: <2 seconds per request
- **Success Rate**: >85% for Paris addresses
- **Cost**: Within Mapbox free tier limits

## Test Data Sources

- Use sample data from `n8n/sample-data/`
- Real Instagram captions from test profiles
- Generated test addresses for edge cases

## Reporting

After testing, document:
- Success/failure rates
- Common failure patterns
- Performance metrics
- Recommendations for improvements

## Related Files

- `geocoding-setup.md`: Setup instructions
- `geocoding-workflow-update.md`: Update procedure
- `n8n/sample-data/`: Test data files