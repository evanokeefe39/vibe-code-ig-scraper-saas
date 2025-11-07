// Explode Array Items Node for n8n
// Takes an array field and creates separate items for each element

const items = $input.all();
const explodedItems = [];

// Get the field name to explode from node parameters
const fieldName = $node.parameter.fieldName || 'sources';

items.forEach(item => {
  const arrayToExplode = item.json[fieldName];
    
      if (Array.isArray(arrayToExplode)) {
          arrayToExplode.forEach((arrayItem, index) => {
                // Create new item with the exploded array item
                      // Keep all other fields from original item
                            const newItem = {
                                    ...item.json,
                                            [fieldName]: arrayItem,
                                                    [fieldName + '_index']: index, // Optional: add original index
                                                            [fieldName + '_count']: arrayToExplode.length // Optional: add total count
                                                                  };
                                                                        
                                                                              explodedItems.push(newItem);
                                                                                  });
                                                                                    } else {
                                                                                        // If not an array, pass through original item
                                                                                            explodedItems.push(item.json);
                                                                                              }
                                                                                              });

                                                                                              return explodedItems;