// Aggregate all incoming items into a single JSON array
// This code is for use in an n8n Code node to collect location data
// and prepare it for updating core_run.output

// Assuming each item.json contains a location object
const locations = items.map(item => item.json);

// Return a single item with the aggregated array
return [{
  json: {
    output: locations
  }
}];