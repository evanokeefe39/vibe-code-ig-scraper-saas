import json
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class ExtractionService:
    """Service for enhanced LLM-based data extraction from multi-platform scraped data"""
    
    def __init__(self):
        self.platform_field_mappings = {
            'instagram': {
                'caption': ['caption', 'text', 'description'],
                'likes': ['like_count', 'likes', 'likeCount'],
                'comments': ['comment_count', 'comments', 'commentCount'],
                'shares': ['share_count', 'shares'],
                'views': ['view_count', 'views', 'viewCount'],
                'author': ['owner_username', 'author', 'username'],
                'media_url': ['display_url', 'url', 'media_url'],
                'media_type': ['media_type', 'type'],
                'timestamp': ['taken_at', 'timestamp', 'created_time'],
                'location': ['location', 'place'],
                'hashtags': ['hashtags', 'tags'],
                'mentions': ['mentions', 'user_tags']
            },
            'tiktok': {
                'caption': ['text', 'description', 'caption'],
                'likes': ['diggCount', 'likes', 'like_count'],
                'comments': ['commentCount', 'comments', 'comment_count'],
                'shares': ['shareCount', 'shares', 'share_count'],
                'views': ['playCount', 'views', 'view_count'],
                'author': ['authorMeta.name', 'username', 'author'],
                'media_url': ['webVideoUrl', 'url', 'media_url'],
                'media_type': ['type', 'media_type'],
                'timestamp': ['createTime', 'timestamp', 'created_time'],
                'location': ['location', 'place'],
                'hashtags': ['hashtags', 'tags'],
                'mentions': ['mentions', 'user_tags']
            },
            'youtube': {
                'caption': ['description', 'title', 'caption'],
                'likes': ['likeCount', 'likes', 'like_count'],
                'comments': ['commentCount', 'comments', 'comment_count'],
                'shares': ['share_count', 'shares'],
                'views': ['viewCount', 'views', 'view_count'],
                'author': ['channelTitle', 'author', 'username'],
                'media_url': ['url', 'webUrl', 'media_url'],
                'media_type': ['type', 'media_type'],
                'timestamp': ['publishedAt', 'timestamp', 'created_time'],
                'location': ['location', 'place'],
                'hashtags': ['hashtags', 'tags'],
                'mentions': ['mentions', 'user_tags']
            }
        }
    
    def create_extraction_prompt(self, base_prompt: str, platforms: List[str], sample_data: Dict[str, List[Dict]]) -> str:
        """Create enhanced extraction prompt based on platforms and sample data"""
        
        # Analyze available fields in sample data
        available_fields = self._analyze_available_fields(sample_data)
        
        # Build platform-specific instructions
        platform_instructions = []
        for platform in platforms:
            if platform in self.platform_field_mappings:
                fields = self.platform_field_mappings[platform]
                platform_instruction = f"""
For {platform.title()} data:
- Look for common fields: {', '.join(fields.keys())}
- Handle platform-specific field names: {', '.join([f'{k}: {v}' for k, v in fields.items() if v])}
- Extract location data from geotags, text mentions, or profile locations
- Identify business mentions, contact information, and commercial content
"""
                platform_instructions.append(platform_instruction)
        
        # Build field mapping instructions
        field_mapping_instructions = self._build_field_mapping_instructions(available_fields)
        
        enhanced_prompt = f"""
{base_prompt}

PLATFORM-SPECIFIC INSTRUCTIONS:
{chr(10).join(platform_instructions)}

FIELD MAPPING INSTRUCTIONS:
{field_mapping_instructions}

DATA STRUCTURE GUIDELINES:
- Extract structured data that can be organized in tables
- Use consistent field names across platforms
- Handle missing data gracefully (use null or empty strings)
- Preserve original data types (numbers, dates, URLs)
- Extract nested data into flat structure where possible

QUALITY REQUIREMENTS:
- Validate extracted data against source
- Ensure data consistency across platforms
- Flag uncertain or low-confidence extractions
- Provide confidence scores where possible

OUTPUT FORMAT:
Return extracted data as JSON array of objects with consistent field names.
"""
        
        return enhanced_prompt
    
    def _analyze_available_fields(self, sample_data: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
        """Analyze sample data to identify available fields"""
        available_fields = {}
        
        for platform, items in sample_data.items():
            if not items:
                continue
                
            platform_fields = set()
            # Analyze first few items to identify fields
            for item in items[:5]:  # Sample first 5 items
                if isinstance(item, dict):
                    platform_fields.update(self._extract_all_keys(item))
            
            available_fields[platform] = list(platform_fields)
        
        return available_fields
    
    def _extract_all_keys(self, obj: Any, prefix: str = '') -> List[str]:
        """Recursively extract all keys from nested object"""
        keys = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                if isinstance(value, (dict, list)):
                    keys.extend(self._extract_all_keys(value, full_key))
        elif isinstance(obj, list) and obj:
            # Analyze first item in array
            keys.extend(self._extract_all_keys(obj[0], prefix))
        
        return keys
    
    def _build_field_mapping_instructions(self, available_fields: Dict[str, List[str]]) -> str:
        """Build instructions for mapping platform-specific fields"""
        instructions = []
        
        for platform, fields in available_fields.items():
            if platform in self.platform_field_mappings:
                mapping = self.platform_field_mappings[platform]
                platform_instructions = []
                
                for standard_field, platform_variants in mapping.items():
                    found_variants = [v for v in platform_variants if v in fields]
                    if found_variants:
                        platform_instructions.append(f"  {standard_field}: {found_variants}")
                
                if platform_instructions:
                    instructions.append(f"{platform.title()} field mappings:")
                    instructions.extend(platform_instructions)
        
        return '\n'.join(instructions) if instructions else "Use standard field names based on data analysis."
    
    def extract_entities(self, scraped_data: Dict[str, List[Dict]], extraction_prompt: str, platforms: List[str]) -> Dict[str, Any]:
        """Extract entities from multi-platform scraped data"""
        
        try:
            # Prepare sample data for prompt enhancement
            sample_data = {}
            for platform, items in scraped_data.items():
                if items:
                    sample_data[platform] = items[:3]  # Use first 3 items as sample
            
            # Create enhanced prompt
            enhanced_prompt = self.create_extraction_prompt(extraction_prompt, platforms, sample_data)
            
            # Combine all scraped data for extraction
            all_items = []
            for platform, items in scraped_data.items():
                for item in items:
                    # Add platform metadata
                    item_with_platform = item.copy()
                    item_with_platform['_platform'] = platform
                    all_items.append(item_with_platform)
            
            # Here you would integrate with your LLM service
            # For now, return a placeholder structure
            extracted_data = {
                'entities': [],
                'metadata': {
                    'total_items': len(all_items),
                    'platforms': platforms,
                    'extraction_prompt': enhanced_prompt,
                    'field_mappings': self._get_field_mappings_for_platforms(platforms)
                }
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in extraction service: {str(e)}")
            return {
                'entities': [],
                'error': str(e),
                'metadata': {
                    'platforms': platforms,
                    'extraction_prompt': extraction_prompt
                }
            }
    
    def _get_field_mappings_for_platforms(self, platforms: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Get field mappings for specified platforms"""
        return {platform: self.platform_field_mappings.get(platform, {}) 
                for platform in platforms}
    
    def infer_columns_from_data(self, scraped_data: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Infer column definitions from scraped data structure"""
        
        columns = []
        all_fields = set()
        field_samples = {}
        
        # Collect all fields and sample values
        for platform, items in scraped_data.items():
            if not items:
                continue
                
            for item in items[:10]:  # Sample first 10 items
                for field, value in self._flatten_dict(item).items():
                    all_fields.add(field)
                    if field not in field_samples:
                        field_samples[field] = []
                    field_samples[field].append(value)
        
        # Analyze each field to determine column type
        for field in sorted(all_fields):
            samples = field_samples[field][:5]  # Use first 5 samples
            column_type = self._infer_column_type(field, samples)
            
            columns.append({
                'name': field,
                'column_type': column_type,
                'description': self._generate_field_description(field, samples),
                'required': False,
                'order': len(columns)
            })
        
        return columns
    
    def _flatten_dict(self, obj: Any, prefix: str = '', separator: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        result = {}
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}{separator}{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    result.update(self._flatten_dict(value, new_key, separator))
                else:
                    result[new_key] = value
        elif isinstance(obj, list) and obj:
            # For arrays, use the first item's structure
            result.update(self._flatten_dict(obj[0], prefix, separator))
        else:
            result[prefix] = obj
        
        return result
    
    def _infer_column_type(self, field: str, samples: List[Any]) -> str:
        """Infer column type from field name and sample values"""
        # Check field name patterns
        field_lower = field.lower()
        
        if any(keyword in field_lower for keyword in ['url', 'link', 'web', 'media']):
            return 'url'
        elif any(keyword in field_lower for keyword in ['count', 'number', 'amount', 'total']):
            return 'number'
        elif any(keyword in field_lower for keyword in ['date', 'time', 'created', 'published', 'taken']):
            return 'date'
        elif any(keyword in field_lower for keyword in ['is_', 'has_', 'can_', 'should_']):
            return 'boolean'
        elif any(keyword in field_lower for keyword in ['json', 'metadata', 'data']):
            return 'json'
        
        # Analyze sample values
        non_null_samples = [s for s in samples if s is not None and s != '']
        if not non_null_samples:
            return 'text'
        
        # Check if all samples are numbers
        if all(isinstance(s, (int, float)) or (isinstance(s, str) and s.replace('.', '').replace('-', '').isdigit()) 
               for s in non_null_samples):
            return 'number'
        
        # Check if all samples are URLs
        if all(isinstance(s, str) and ('http://' in s or 'https://' in s) for s in non_null_samples):
            return 'url'
        
        # Check if all samples are boolean-like
        if all(str(s).lower() in ['true', 'false', 'yes', 'no', '1', '0'] for s in non_null_samples):
            return 'boolean'
        
        # Default to text
        return 'text'
    
    def _generate_field_description(self, field: str, samples: List[Any]) -> str:
        """Generate description for field based on name and samples"""
        field_lower = field.lower()
        
        # Common field descriptions
        descriptions = {
            'caption': 'Post caption or text content',
            'likes': 'Number of likes',
            'comments': 'Number of comments',
            'shares': 'Number of shares',
            'views': 'Number of views',
            'author': 'Author or creator username',
            'username': 'Username of the creator',
            'media_url': 'URL to media content',
            'url': 'URL link',
            'timestamp': 'Publication timestamp',
            'created_time': 'Time when content was created',
            'location': 'Geographic location',
            'hashtags': 'Hashtags used in the post',
            'mentions': 'User mentions in the post'
        }
        
        # Check for exact matches
        if field_lower in descriptions:
            return descriptions[field_lower]
        
        # Check for partial matches
        for key, desc in descriptions.items():
            if key in field_lower or field_lower in key:
                return desc
        
        # Generate description from field name
        if 'count' in field_lower:
            return f'Number of {field_lower.replace("_count", "").replace("count", "")}'
        elif 'is_' in field_lower:
            return f'Whether the item {field_lower.replace("is_", "")}'
        elif 'has_' in field_lower:
            return f'Whether the item has {field_lower.replace("has_", "")}'
        else:
            # Generate from field name
            return field.replace('_', ' ').title()
    
    def validate_extraction_quality(self, extracted_data: Dict[str, Any], original_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Validate quality of extracted data against original"""
        
        validation_result = {
            'is_valid': True,
            'issues': [],
            'quality_score': 1.0,
            'statistics': {}
        }
        
        try:
            entities = extracted_data.get('entities', [])
            original_count = sum(len(items) for items in original_data.values())
            extracted_count = len(entities)
            
            # Check extraction completeness
            if extracted_count == 0:
                validation_result['is_valid'] = False
                validation_result['issues'].append('No entities extracted')
                validation_result['quality_score'] = 0.0
            elif extracted_count < original_count * 0.5:  # Less than 50% extracted
                validation_result['issues'].append(f'Low extraction rate: {extracted_count}/{original_count}')
                validation_result['quality_score'] = min(0.5, extracted_count / original_count)
            
            # Check data consistency
            if entities:
                # Check for required fields
                sample_entity = entities[0]
                missing_critical_fields = []
                
                critical_fields = ['caption', 'author', 'timestamp']
                for field in critical_fields:
                    if field not in sample_entity or not sample_entity[field]:
                        missing_critical_fields.append(field)
                
                if missing_critical_fields:
                    validation_result['issues'].append(f'Missing critical fields: {missing_critical_fields}')
                    validation_result['quality_score'] *= 0.8
            
            validation_result['statistics'] = {
                'original_items': original_count,
                'extracted_entities': extracted_count,
                'extraction_rate': extracted_count / original_count if original_count > 0 else 0,
                'platforms_processed': list(original_data.keys())
            }
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f'Validation error: {str(e)}')
            validation_result['quality_score'] = 0.0
        
        return validation_result