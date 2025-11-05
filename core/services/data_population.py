import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

class DataPopulationService:
    """Service for populating data from scraped to extracted format with column inference"""
    
    def __init__(self):
        self.platform_field_mappings = {
            'instagram': {
                'primary_fields': {
                    'caption': ['caption', 'text', 'edge_media_to_caption.edges.0.node.text'],
                    'likes': ['like_count', 'edge_liked_by.count', 'likes'],
                    'comments': ['comment_count', 'edge_media_to_comment.count', 'comments'],
                    'author': ['owner.username', 'owner.username', 'author'],
                    'media_url': ['display_url', 'url', 'image_url'],
                    'media_type': ['media_type', '__typename'],
                    'timestamp': ['taken_at', 'timestamp', 'date'],
                    'location': ['location.name', 'location'],
                    'hashtags': ['hashtags', 'tags'],
                    'mentions': ['usertags.in', 'mentions']
                },
                'engagement_fields': {
                    'views': ['view_count', 'video_view_count'],
                    'shares': ['share_count']
                }
            },
            'tiktok': {
                'primary_fields': {
                    'caption': ['text', 'description', 'caption'],
                    'likes': ['diggCount', 'likes', 'like_count'],
                    'comments': ['commentCount', 'comments', 'comment_count'],
                    'author': ['authorMeta.name', 'authorMeta.id', 'username'],
                    'media_url': ['webVideoUrl', 'videoUrl', 'url'],
                    'media_type': ['type', 'media_type'],
                    'timestamp': ['createTime', 'timestamp', 'date'],
                    'location': ['location', 'place'],
                    'hashtags': ['hashtags', 'tags'],
                    'mentions': ['mentions', 'user_tags']
                },
                'engagement_fields': {
                    'views': ['playCount', 'views', 'view_count'],
                    'shares': ['shareCount', 'shares', 'share_count']
                }
            },
            'youtube': {
                'primary_fields': {
                    'caption': ['description', 'title', 'caption'],
                    'likes': ['likeCount', 'likes', 'like_count'],
                    'comments': ['commentCount', 'comments', 'comment_count'],
                    'author': ['channelTitle', 'channelId', 'author'],
                    'media_url': ['url', 'webUrl', 'video_url'],
                    'media_type': ['type', 'media_type'],
                    'timestamp': ['publishedAt', 'timestamp', 'date'],
                    'location': ['location', 'place'],
                    'hashtags': ['hashtags', 'tags'],
                    'mentions': ['mentions', 'user_tags']
                },
                'engagement_fields': {
                    'views': ['viewCount', 'views', 'view_count'],
                    'shares': ['share_count', 'shares']
                }
            }
        }
    
    def infer_columns_from_scraped_data(self, scraped_data: Dict[str, List[Dict]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Infer column definitions from scraped data structure"""
        
        columns = []
        inference_metadata = {
            'total_items_analyzed': 0,
            'platforms_found': list(scraped_data.keys()),
            'field_coverage': {},
            'data_quality': {}
        }
        
        all_fields = {}
        field_samples = {}
        field_types = {}
        
        # Analyze each platform's data
        for platform, items in scraped_data.items():
            if not items:
                continue
            
            inference_metadata['total_items_analyzed'] += len(items)
            platform_mapping = self.platform_field_mappings.get(platform, {})
            
            # Sample items for analysis
            sample_items = items[:min(20, len(items))]  # Analyze up to 20 items per platform
            
            for item in sample_items:
                # Extract all possible fields
                flat_item = self._flatten_dict(item)
                
                for field_name, field_value in flat_item.items():
                    if field_name not in field_samples:
                        field_samples[field_name] = []
                        field_types[field_name] = set()
                    
                    field_samples[field_name].append(field_value)
                    field_types[field_name].add(type(field_value).__name__)
        
        # Generate column definitions
        for field_name in sorted(field_samples.keys()):
            samples = field_samples[field_name][:10]  # Use first 10 samples
            column_type = self._determine_column_type(field_name, samples, field_types[field_name])
            
            # Determine if field is commonly available across platforms
            availability = self._calculate_field_availability(field_name, scraped_data)
            
            column = {
                'name': field_name,
                'column_type': column_type,
                'description': self._generate_column_description(field_name, samples),
                'required': availability > 0.7,  # Required if available in >70% of data
                'order': len(columns),
                'availability': availability,
                'sample_values': [str(s) for s in samples[:3] if s is not None and s != ''],
                'platforms_found': self._find_platforms_for_field(field_name, scraped_data)
            }
            
            columns.append(column)
            
            # Update metadata
            inference_metadata['field_coverage'][field_name] = availability
        
        # Sort columns by availability and importance
        columns.sort(key=lambda x: (-x['availability'], x['name']))
        
        # Update column orders
        for i, column in enumerate(columns):
            column['order'] = i
        
        # Calculate data quality metrics
        inference_metadata['data_quality'] = self._calculate_data_quality(scraped_data, columns)
        
        return columns, inference_metadata
    
    def populate_extracted_data(self, scraped_data: Dict[str, List[Dict]], columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Populate extracted data from scraped data using inferred columns"""
        
        extracted_entities = []
        
        for platform, items in scraped_data.items():
            if not items:
                continue
            
            platform_mapping = self.platform_field_mappings.get(platform, {})
            
            for item in items:
                # Flatten the item for easier field access
                flat_item = self._flatten_dict(item)
                
                # Create entity with platform metadata
                entity = {
                    '_platform': platform,
                    '_source_data': item  # Keep original data for reference
                }
                
                # Populate columns
                for column in columns:
                    field_name = column['name']
                    column_type = column['column_type']
                    
                    # Get value using field mapping
                    value = self._extract_field_value(flat_item, field_name, platform_mapping)
                    
                    # Convert value to appropriate type
                    converted_value = self._convert_value_type(value, column_type)
                    
                    entity[field_name] = converted_value
                
                extracted_entities.append(entity)
        
        return extracted_entities
    
    def _flatten_dict(self, obj: Any, prefix: str = '', separator: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary with dot notation"""
        result = {}
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}{separator}{key}" if prefix else key
                
                if key == 'edges' and isinstance(value, list) and value:
                    # Handle GraphQL edges pattern
                    for i, edge in enumerate(value):
                        if isinstance(edge, dict) and 'node' in edge:
                            edge_key = f"{new_key}{separator}{i}"
                            result.update(self._flatten_dict(edge['node'], edge_key, separator))
                elif isinstance(value, (dict, list)):
                    result.update(self._flatten_dict(value, new_key, separator))
                else:
                    result[new_key] = value
        elif isinstance(obj, list) and obj:
            # For arrays, analyze the first item's structure
            if len(obj) == 1:
                result.update(self._flatten_dict(obj[0], prefix, separator))
            else:
                # For multiple items, create array references
                for i, item in enumerate(obj):
                    item_key = f"{prefix}{separator}{i}"
                    result.update(self._flatten_dict(item, item_key, separator))
        else:
            result[prefix] = obj
        
        return result
    
    def _determine_column_type(self, field_name: str, samples: List[Any], type_hints: set) -> str:
        """Determine the best column type for a field"""
        
        field_lower = field_name.lower()
        
        # Check field name patterns first
        if any(keyword in field_lower for keyword in ['url', 'link', 'web', 'media', 'video', 'image']):
            return 'url'
        elif any(keyword in field_lower for keyword in ['count', 'number', 'amount', 'total', 'views', 'likes', 'comments']):
            return 'number'
        elif any(keyword in field_lower for keyword in ['date', 'time', 'created', 'published', 'taken', 'at']):
            return 'date'
        elif any(keyword in field_lower for keyword in ['is_', 'has_', 'can_', 'should_']):
            return 'boolean'
        elif any(keyword in field_lower for keyword in ['json', 'metadata', 'data', 'config']):
            return 'json'
        
        # Analyze actual data types
        non_null_samples = [s for s in samples if s is not None and s != '']
        if not non_null_samples:
            return 'text'
        
        # Check if all samples are numeric
        numeric_count = 0
        for sample in non_null_samples:
            if isinstance(sample, (int, float)):
                numeric_count += 1
            elif isinstance(sample, str) and sample.replace('.', '').replace('-', '').replace(',', '').isdigit():
                numeric_count += 1
        
        if numeric_count / len(non_null_samples) > 0.8:  # 80% numeric
            return 'number'
        
        # Check if all samples are URLs
        url_count = sum(1 for s in non_null_samples if isinstance(s, str) and ('http://' in s or 'https://' in s))
        if url_count / len(non_null_samples) > 0.8:
            return 'url'
        
        # Check if all samples are boolean-like
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', 'True', 'False'}
        bool_count = sum(1 for s in non_null_samples if str(s) in bool_values)
        if bool_count / len(non_null_samples) > 0.8:
            return 'boolean'
        
        # Check if it's a date
        date_count = 0
        for sample in non_null_samples:
            if self._is_date_like(sample):
                date_count += 1
        
        if date_count / len(non_null_samples) > 0.8:
            return 'date'
        
        # Default to text
        return 'text'
    
    def _is_date_like(self, value: Any) -> bool:
        """Check if value looks like a date"""
        if not isinstance(value, str):
            return False
        
        date_indicators = [
            'T',  # ISO format separator
            '-',  # Date separator
            ':',  # Time separator
            'UTC',
            'GMT',
            '+00:00'
        ]
        
        return any(indicator in value for indicator in date_indicators)
    
    def _generate_column_description(self, field_name: str, samples: List[Any]) -> str:
        """Generate a descriptive column name and description"""
        
        field_lower = field_name.lower()
        
        # Common field mappings
        field_descriptions = {
            'caption': 'Post caption or text content',
            'text': 'Text content of the post',
            'description': 'Description or caption',
            'likes': 'Number of likes',
            'like_count': 'Number of likes',
            'diggcount': 'Number of likes (TikTok)',
            'likecount': 'Number of likes',
            'comments': 'Number of comments',
            'comment_count': 'Number of comments',
            'commentcount': 'Number of comments',
            'shares': 'Number of shares',
            'share_count': 'Number of shares',
            'sharecount': 'Number of shares',
            'views': 'Number of views',
            'view_count': 'Number of views',
            'viewcount': 'Number of views',
            'playcount': 'Number of views (TikTok)',
            'author': 'Author or creator name',
            'username': 'Author username',
            'authormeta.name': 'Author name (TikTok)',
            'channeltitle': 'Channel name (YouTube)',
            'media_url': 'URL to media content',
            'display_url': 'Media display URL',
            'webvideourl': 'Video URL (TikTok)',
            'url': 'URL link',
            'timestamp': 'Publication timestamp',
            'taken_at': 'When the post was created',
            'createtime': 'Creation time (TikTok)',
            'publishedat': 'Publication time (YouTube)',
            'location': 'Geographic location',
            'hashtags': 'Hashtags used',
            'mentions': 'User mentions',
            'usertags': 'User tags'
        }
        
        # Check for exact match
        if field_lower in field_descriptions:
            return field_descriptions[field_lower]
        
        # Generate from field name
        if 'count' in field_lower:
            base_name = field_lower.replace('_count', '').replace('count', '')
            return f'Number of {base_name}'
        elif field_lower.startswith('is_'):
            return f'Whether the item {field_lower[3:]}'
        elif field_lower.startswith('has_'):
            return f'Whether the item has {field_lower[4:]}'
        else:
            # Convert snake_case to readable format
            return field_name.replace('_', ' ').title()
    
    def _calculate_field_availability(self, field_name: str, scraped_data: Dict[str, List[Dict]]) -> float:
        """Calculate how often a field is available across all data"""
        
        total_items = 0
        items_with_field = 0
        
        for platform, items in scraped_data.items():
            if not items:
                continue
            
            total_items += len(items)
            
            for item in items:
                flat_item = self._flatten_dict(item)
                if field_name in flat_item and flat_item[field_name] is not None:
                    items_with_field += 1
        
        return items_with_field / total_items if total_items > 0 else 0.0
    
    def _find_platforms_for_field(self, field_name: str, scraped_data: Dict[str, List[Dict]]) -> List[str]:
        """Find which platforms contain a specific field"""
        
        platforms_found = []
        
        for platform, items in scraped_data.items():
            if not items:
                continue
            
            # Check if any item has this field
            for item in items[:5]:  # Check first 5 items
                flat_item = self._flatten_dict(item)
                if field_name in flat_item and flat_item[field_name] is not None:
                    platforms_found.append(platform)
                    break
        
        return platforms_found
    
    def _extract_field_value(self, flat_item: Dict[str, Any], field_name: str, platform_mapping: Dict[str, Any]) -> Any:
        """Extract field value using platform-specific mappings"""
        
        # Direct field access
        if field_name in flat_item:
            return flat_item[field_name]
        
        # Try platform-specific field mappings
        all_mappings = {}
        if 'primary_fields' in platform_mapping:
            all_mappings.update(platform_mapping['primary_fields'])
        if 'engagement_fields' in platform_mapping:
            all_mappings.update(platform_mapping['engagement_fields'])
        
        if field_name in all_mappings:
            possible_fields = all_mappings[field_name]
            for possible_field in possible_fields:
                if possible_field in flat_item:
                    return flat_item[possible_field]
        
        # Try partial matches
        for key, value in flat_item.items():
            if field_name.lower() in key.lower() or key.lower() in field_name.lower():
                return value
        
        return None
    
    def _convert_value_type(self, value: Any, target_type: str) -> Any:
        """Convert value to the target type"""
        
        if value is None or value == '':
            return None
        
        try:
            if target_type == 'number':
                if isinstance(value, (int, float)):
                    return value
                elif isinstance(value, str):
                    # Clean the string and convert
                    cleaned = value.replace(',', '').replace(' ', '')
                    if '.' in cleaned:
                        return float(cleaned)
                    else:
                        return int(cleaned)
                else:
                    return float(value) if '.' in str(value) else int(value)
            
            elif target_type == 'date':
                if isinstance(value, str):
                    # Try to parse common date formats
                    date_formats = [
                        '%Y-%m-%dT%H:%M:%S.%fZ',
                        '%Y-%m-%dT%H:%M:%SZ',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d',
                        '%Y-%m-%dT%H:%M:%S%z'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    
                    # If no format matches, return original string
                    return value
                else:
                    return value
            
            elif target_type == 'boolean':
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ['true', 'yes', '1', 'on']
                elif isinstance(value, (int, float)):
                    return bool(value)
                else:
                    return bool(value)
            
            elif target_type == 'url':
                if isinstance(value, str):
                    # Ensure it's a valid URL format
                    if not value.startswith(('http://', 'https://')):
                        return f"https://{value}"
                    return value
                else:
                    return str(value)
            
            else:  # text, json, select, multi_select
                return value
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Error converting value {value} to {target_type}: {e}")
            return value  # Return original value if conversion fails
    
    def _calculate_data_quality(self, scraped_data: Dict[str, List[Dict]], columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        
        quality_metrics = {
            'completeness': 0.0,
            'consistency': 0.0,
            'validity': 0.0,
            'overall_score': 0.0,
            'issues': []
        }
        
        total_items = sum(len(items) for items in scraped_data.values())
        if total_items == 0:
            return quality_metrics
        
        # Calculate completeness (percentage of non-null values)
        total_fields = len(columns) * total_items
        non_null_fields = 0
        
        for platform, items in scraped_data.items():
            for item in items:
                flat_item = self._flatten_dict(item)
                for column in columns:
                    field_name = column['name']
                    if field_name in flat_item and flat_item[field_name] is not None:
                        non_null_fields += 1
        
        quality_metrics['completeness'] = non_null_fields / total_fields if total_fields > 0 else 0.0
        
        # Calculate consistency (similar data types across platforms)
        consistency_scores = []
        for column in columns:
            field_name = column['name']
            types_per_platform = {}
            
            for platform, items in scraped_data.items():
                if not items:
                    continue
                
                platform_types = set()
                for item in items[:10]:  # Sample first 10 items
                    flat_item = self._flatten_dict(item)
                    if field_name in flat_item:
                        platform_types.add(type(flat_item[field_name]).__name__)
                
                if platform_types:
                    types_per_platform[platform] = platform_types
            
            # Score based on type consistency across platforms
            if len(types_per_platform) <= 1:
                consistency_scores.append(1.0)
            else:
                all_types = set()
                for types in types_per_platform.values():
                    all_types.update(types)
                consistency_scores.append(1.0 / len(all_types))
        
        quality_metrics['consistency'] = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
        
        # Calculate validity (proper URL formats, valid dates, etc.)
        validity_scores = []
        for column in columns:
            field_name = column['name']
            column_type = column['column_type']
            
            valid_count = 0
            total_count = 0
            
            for platform, items in scraped_data.items():
                for item in items[:10]:  # Sample first 10 items
                    flat_item = self._flatten_dict(item)
                    if field_name in flat_item and flat_item[field_name] is not None:
                        total_count += 1
                        if self._is_valid_value(flat_item[field_name], column_type):
                            valid_count += 1
            
            if total_count > 0:
                validity_scores.append(valid_count / total_count)
        
        quality_metrics['validity'] = sum(validity_scores) / len(validity_scores) if validity_scores else 0.0
        
        # Calculate overall score
        quality_metrics['overall_score'] = (
            quality_metrics['completeness'] * 0.4 +
            quality_metrics['consistency'] * 0.3 +
            quality_metrics['validity'] * 0.3
        )
        
        # Identify issues
        if quality_metrics['completeness'] < 0.5:
            quality_metrics['issues'].append('Low data completeness')
        if quality_metrics['consistency'] < 0.7:
            quality_metrics['issues'].append('Inconsistent data types across platforms')
        if quality_metrics['validity'] < 0.8:
            quality_metrics['issues'].append('Invalid data formats detected')
        
        return quality_metrics
    
    def _is_valid_value(self, value: Any, expected_type: str) -> bool:
        """Check if a value is valid for its expected type"""
        
        if expected_type == 'url':
            return isinstance(value, str) and ('http://' in value or 'https://' in value)
        elif expected_type == 'number':
            return isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit())
        elif expected_type == 'date':
            return self._is_date_like(value)
        elif expected_type == 'boolean':
            return isinstance(value, bool) or str(value).lower() in ['true', 'false', 'yes', 'no', '1', '0']
        else:
            return True  # text, json, select, multi_select are generally valid