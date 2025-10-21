// Robust JSON Parser for LLM Output in n8n
// Use in a Function node after Basic LLM Chain
// Now handles arrays of location objects

function parseLLMJson(text) {
  if (!text || typeof text !== 'string') {
    return createFallbackResult('Invalid input: text is empty or not a string');
  }

  // Clean the text - remove markdown code blocks if present
  let cleanText = text.trim();

  // Remove markdown code block markers
  if (cleanText.startsWith('```json')) {
    cleanText = cleanText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
  } else if (cleanText.startsWith('```')) {
    cleanText = cleanText.replace(/^```\s*/, '').replace(/\s*```$/, '');
  }

  // Try direct JSON parse first
  try {
    const parsed = JSON.parse(cleanText);
    return validateResult(parsed);
  } catch (e) {
    // If direct parse fails, try to extract JSON from text
    console.log('Direct JSON parse failed, attempting extraction:', e.message);

    // Look for JSON array structure in the text
    const jsonMatch = cleanText.match(/\[[\s\S]*\]/);
    if (jsonMatch) {
      try {
        const extractedJson = JSON.parse(jsonMatch[0]);
        return validateResult(extractedJson);
      } catch (e2) {
        console.log('JSON array extraction failed:', e2.message);
      }
    }

    // Fallback: look for single object
    const objectMatch = cleanText.match(/\{[\s\S]*\}/);
    if (objectMatch) {
      try {
        const extractedJson = JSON.parse(objectMatch[0]);
        // Wrap single object in array for consistency
        return validateResult([extractedJson]);
      } catch (e2) {
        console.log('JSON object extraction failed:', e2.message);
      }
    }

    // Last resort: try to fix common JSON issues
    try {
      // Remove trailing commas, fix quotes, etc.
      let fixedText = cleanText
        .replace(/,\s*}/g, '}')  // Remove trailing commas
        .replace(/,\s*]/g, ']')  // Remove trailing commas in arrays
        .replace(/([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g, '$1"$2":')  // Quote unquoted keys
        .replace(/:\s*'([^']*)'/g, ':"$1"')  // Convert single quotes to double
        .replace(/:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}\]])/g, ':"$1"$2'); // Quote unquoted string values

      const parsed = JSON.parse(fixedText);
      return validateResult(parsed);
    } catch (e3) {
      console.log('JSON fixing failed:', e3.message);
      return [createFallbackResult(`JSON parsing failed: ${e.message}. Raw text: ${cleanText.substring(0, 200)}`)];
    }
  }
}

function validateResult(result) {
  // Handle both single objects and arrays
  let locations = result;

  // If result is a single object, wrap it in an array
  if (!Array.isArray(result)) {
    locations = [result];
  }

  // Validate and clean each location object
  const validatedLocations = locations.map((location, index) => {
    if (!location || typeof location !== 'object') {
      console.warn(`Invalid location at index ${index}, using fallback`);
      return createFallbackResult(`Invalid location object at index ${index}`);
    }

    // Validate expected structure
    const requiredFields = ['address', 'category', 'vibes', 'cost_note', 'confidence'];

    for (const field of requiredFields) {
      if (!(field in location)) {
        console.warn(`Missing required field '${field}' in location ${index}`);
        // Don't fail, just warn - LLM might omit fields
      }
    }

    // Ensure vibes is an array
    if (location.vibes && !Array.isArray(location.vibes)) {
      location.vibes = [location.vibes];
    }

    // Ensure confidence is a number
    if (typeof location.confidence !== 'number') {
      location.confidence = parseFloat(location.confidence) || 0.5;
    }

    // Ensure business_name is present (can be null)
    if (!('business_name' in location)) {
      location.business_name = null;
    }

    return location;
  });

  return validatedLocations;
}

function createFallbackResult(error) {
  return {
    business_name: null,
    address: null,
    category: 'other',
    vibes: ['neutral'],
    cost_note: 'unknown',
    confidence: 0.0,
    error: error
  };
}

// Main execution for n8n Function node
const llmOutput = $input.item.json.text || $input.item.json.response || $input.item.json.output;
const parsedLocations = parseLLMJson(llmOutput);


// Return each location as a separate n8n item
return {json: {locations: parsedLocations}};