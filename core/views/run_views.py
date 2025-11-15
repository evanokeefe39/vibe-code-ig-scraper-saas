import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Run, UserList, ListColumn, ListRow
from ..forms import RunForm, SourceFormSet
from ..services.n8n_service import get_n8n_execution_status, build_source_config, trigger_run


@login_required
def run_create(request):
    if request.method == 'POST':
        source_formset = SourceFormSet(request.POST, prefix='form')
        form = RunForm(request.POST)
        
        sources = []
        
        # Process sources from formset
        if source_formset.is_valid():
            for source_form in source_formset:
                if source_form.is_valid() and source_form.cleaned_data.get('source_type'):
                    source_type = source_form.cleaned_data['source_type']
                    source_config = build_source_config(source_form.cleaned_data)
                    
                    # Extract platform from sourceType
                    if source_type.startswith('youtube-'):
                        platform = 'youtube'
                    elif source_type.startswith('instagram-'):
                        platform = 'instagram'
                    elif source_type.startswith('tiktok-'):
                        platform = 'tiktok'
                    else:
                        platform = 'unknown'
                    
                    sources.append({
                        "sourceType": source_type,
                        "platform": platform,
                        "config": source_config
                    })
            
            # Populate the sources field in the form for validation
            form.data = form.data.copy()
            try:
                form.data['sources'] = json.dumps(sources)
            except (TypeError, ValueError) as e:
                # Debug: log the problematic data
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"JSON serialization error: {e}")
                logger.error(f"Sources data: {sources}")
                # Try to fix date objects by converting them to strings
                def serialize_dates(obj):
                    if hasattr(obj, 'strftime'):
                        return obj.strftime('%Y-%m-%d')
                    elif isinstance(obj, dict):
                        return {k: serialize_dates(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [serialize_dates(item) for item in obj]
                    return obj
                
                sources = serialize_dates(sources)
                form.data['sources'] = json.dumps(sources)
        
        # Validate both forms and create run
        if source_formset.is_valid() and form.is_valid():
            # Create run with processed sources
            run = form.save(commit=False)
            run.user_id = request.user.id
            # Helper function to serialize any date objects
            def serialize_dates(obj):
                if hasattr(obj, 'strftime'):
                    return obj.strftime('%Y-%m-%d')
                elif isinstance(obj, dict):
                    return {k: serialize_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_dates(item) for item in obj]
                return obj
            
            # Serialize sources to handle any date objects
            sources = serialize_dates(sources)
            
            run.input = json.dumps({
                'sources': sources
            })
            run.save()
            trigger_run(run)
            messages.success(request, 'Run started successfully!')
            return redirect('run_detail', pk=run.pk)
    else:
        source_formset = SourceFormSet(prefix='form')
        form = RunForm()
    
    return render(request, 'core/run_create.html', {
        'form': form,
        'source_formset': source_formset
    })


def empty_source_form(request):
    """Return empty form for dynamic formset addition"""
    empty_formset = SourceFormSet(prefix='form')
    empty_form = empty_formset.empty_form
    
    return render(request, 'core/run_create/partials/empty_source_card.html', {
        'form': empty_form
    })


def platform_config(request, platform_type):
    """Return platform-specific configuration HTML"""
    template_map = {
        'youtube-search': 'core/run_create/platforms/youtube_search.html',
        'youtube-channel': 'core/run_create/platforms/youtube_channel.html',
        'youtube-playlist': 'core/run_create/platforms/youtube_playlist.html',
        'youtube-hashtag': 'core/run_create/platforms/youtube_hashtag.html',
        'youtube-video': 'core/run_create/platforms/youtube_video.html',
        'instagram-profile': 'core/run_create/platforms/instagram_profile.html',
        'instagram-post': 'core/run_create/platforms/instagram_post.html',
        'instagram-hashtag': 'core/run_create/platforms/instagram_hashtag.html',
        'instagram-search': 'core/run_create/platforms/instagram_search.html',
        'tiktok-profile': 'core/run_create/platforms/tiktok_profile.html',
        'tiktok-hashtag': 'core/run_create/platforms/tiktok_hashtag.html',
        'tiktok-search': 'core/run_create/platforms/tiktok_search.html',
        'tiktok-video': 'core/run_create/platforms/tiktok_video.html'
    }
    
    template_name = template_map.get(platform_type)
    if not template_name:
        return HttpResponse('<div class="text-red-600">Invalid platform type</div>', status=400)
    
    # Create a form instance with the platform-specific fields
    form = SourceForm(prefix='__prefix__')
    form.source_type = platform_type  # Set the source type
    
    return render(request, template_name, {'form': form})


@login_required
def run_list(request):
    # Filter by authenticated user
    runs = Run.objects.filter(user_id=request.user.id).order_by('-created_at')

    # Add execution status to each run
    runs_with_status = []
    for run in runs:
        execution_info = get_n8n_execution_status(run.n8n_execution_id)
        runs_with_status.append({
            'run': run,
            'status': execution_info['status']
        })

    return render(request, 'core/run_list.html', {'runs_with_status': runs_with_status})


@login_required
def run_detail(request, pk):
    run = get_object_or_404(Run, pk=pk, user_id=request.user.id)
    execution_info = get_n8n_execution_status(run.n8n_execution_id)
    execution_data_json = json.dumps(execution_info['data'])

    # Parse input data
    try:
        if isinstance(run.input, str):
            input_data = json.loads(run.input)
        else:
            input_data = run.input or {}
    except (json.JSONDecodeError, TypeError):
        input_data = {}

    # Prepare input data for JavaScript
    input_json = json.dumps(input_data, indent=2)

    # Prepare data for display - handle both new multi-source and legacy formats
    run_data = {}
    
    # Handle new multi-source format
    if run.scraped and isinstance(run.scraped, dict):
        # New format: scraped data organized by platform
        run_data['scraped_by_platform'] = run.scraped
        # Also create flattened view for compatibility
        all_scraped = []
        for platform, items in run.scraped.items():
            if isinstance(items, list):
                for item in items:
                    all_scraped.append({
                        'platform': platform,
                        'data': item
                    })
        run_data['scraped'] = all_scraped
    elif run.scraped:
        # Legacy format or mixed format
        run_data['scraped'] = run.scraped

    if run.extracted:
        run_data['extracted'] = run.extracted
        
        # Extract metadata if available
        if isinstance(run.extracted, dict) and 'metadata' in run.extracted:
            run_data['extraction_metadata'] = run.extracted['metadata']

    if run.output:
        run_data['legacy_output'] = run.output

    run_data_json = json.dumps(run_data, indent=2) if run_data else 'null'

    # Parse sources for display
    sources = input_data.get('sources', [])
    sources_by_platform = {}
    for source in sources:
        platform = source.get('platform', 'unknown')
        if platform not in sources_by_platform:
            sources_by_platform[platform] = []
        sources_by_platform[platform].append(source)

    return render(request, 'core/run_detail.html', {
        'run': run,
        'execution_status': execution_info['status'],
        'execution_data': execution_info['data'],
        'execution_data_json': execution_data_json,
        'input_data': input_data,
        'input_json': input_json,
        'run_data': run_data,
        'run_data_json': run_data_json,
        'sources': sources,
        'sources_by_platform': sources_by_platform,
        'sources_json': json.dumps(sources, indent=2),
        'run_scraped_json': json.dumps(run.scraped, indent=2) if run.scraped else None,
        'run_extracted_json': json.dumps(run.extracted, indent=2) if run.extracted else None
    })


def run_by_n8n(request, n8n_execution_id):
    run = get_object_or_404(Run, n8n_execution_id=n8n_execution_id)
    execution_info = get_n8n_execution_status(run.n8n_execution_id)
    execution_data_json = json.dumps(execution_info['data'])

    # Prepare data for display - show both new and legacy formats
    run_data = {}
    if run.scraped:
        run_data['scraped'] = run.scraped
    if run.extracted:
        run_data['extracted'] = run.extracted
    if run.output:
        run_data['legacy_output'] = run.output

    run_data_json = json.dumps(run_data) if run_data else 'null'

    return render(request, 'core/run_detail.html', {
        'run': run,
        'execution_status': execution_info['status'],
        'execution_data': execution_info['data'],
        'execution_data_json': execution_data_json,
        'run_data': run_data,
        'run_data_json': run_data_json
    })


def run_status_api(request, pk):
    run = get_object_or_404(Run, pk=pk)
    execution_info = get_n8n_execution_status(run.n8n_execution_id)

    # Include run data in API response
    run_data = {}
    if run.scraped:
        run_data['scraped'] = run.scraped
    if run.extracted:
        run_data['extracted'] = run.extracted
    if run.output:
        run_data['legacy_output'] = run.output

    return JsonResponse({
        'status': execution_info['status'],
        'data': execution_info['data'],
        'run_data': run_data
    })


def parse_extracted_data(extracted_json):
    """Parse extracted data from various formats into a list of entities"""
    if not extracted_json:
        return []
    
    # Handle different data structures
    if isinstance(extracted_json, str):
        try:
            extracted_data = json.loads(extracted_json)
        except json.JSONDecodeError:
            return []
    else:
        extracted_data = extracted_json
    
    # Extract entities from different possible structures
    entities = []
    
    if isinstance(extracted_data, dict):
        # Check for common result keys
        for result_key in ['result', 'results', 'output', 'data']:
            if result_key in extracted_data:
                result_data = extracted_data[result_key]
                if isinstance(result_data, list):
                    entities = result_data
                    break
                elif isinstance(result_data, dict) and 'results' in result_data:
                    entities = result_data['results']
                    break
                elif isinstance(result_data, dict) and 'result' in result_data:
                    entities = result_data['result']
                    break
        
        # If no standard structure found, treat the dict itself as an entity
        if not entities:
            entities = [extracted_data]
    elif isinstance(extracted_data, list):
        entities = extracted_data
    
    return entities


def detect_column_type(sample_values):
    """Detect the most appropriate column type from sample values"""
    if not sample_values:
        return 'text'
    
    # Filter out None/empty values
    non_null_values = [v for v in sample_values if v is not None and v != '']
    
    if not non_null_values:
        return 'text'
    
    # Check for boolean values
    if all(str(v).lower() in ['true', 'false', '1', '0', 'yes', 'no'] for v in non_null_values):
        return 'boolean'
    
    # Check for numeric values
    numeric_count = 0
    for v in non_null_values:
        try:
            float(str(v))
            numeric_count += 1
        except (ValueError, TypeError):
            pass
    
    if numeric_count / len(non_null_values) > 0.8:  # 80% numeric
        return 'number'
    
    # Check for URLs
    url_count = 0
    for v in non_null_values:
        if isinstance(v, str) and ('http://' in v or 'https://' in v):
            url_count += 1
    
    if url_count / len(non_null_values) > 0.5:  # 50% URLs
        return 'url'
    
    # Check for dates
    date_count = 0
    for v in non_null_values:
        if is_date_string(str(v)):
            date_count += 1
    
    if date_count / len(non_null_values) > 0.5:  # 50% dates
        return 'date'
    
    # Check for JSON/objects
    object_count = 0
    for v in non_null_values:
        if isinstance(v, (dict, list)):
            object_count += 1
    
    if object_count / len(non_null_values) > 0.3:  # 30% objects
        return 'json'
    
    # Default to text
    return 'text'


def is_date_string(value):
    """Check if a string looks like a date"""
    from datetime import datetime
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%b %d, %Y',
        '%d %b %Y'
    ]
    
    for fmt in date_formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def is_type_compatible(detected_type, existing_type):
    """Check if detected type is compatible with existing column type"""
    compatibility_map = {
        'text': ['text', 'url', 'json'],
        'number': ['number', 'text'],
        'date': ['date', 'text'],
        'boolean': ['boolean', 'text'],
        'url': ['url', 'text'],
        'json': ['json', 'text']
    }
    
    return existing_type in compatibility_map.get(detected_type, ['text'])


def convert_value_to_column_type(value, column_type):
    """Convert a value to the appropriate type for the column"""
    if value is None or value == '':
        return None
    
    try:
        if column_type == 'number':
            return float(value)
        elif column_type == 'boolean':
            if isinstance(value, bool):
                return value
            return str(value).lower() in ['true', '1', 'yes', 'on']
        elif column_type == 'date':
            from datetime import datetime
            if isinstance(value, str):
                # Try to parse common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(value, fmt).date().isoformat()
                    except ValueError:
                        continue
            return str(value)  # Fallback
        elif column_type == 'url':
            if isinstance(value, str) and not value.startswith(('http://', 'https://')):
                return f'https://{value}'
            return str(value)
        else:
            # text, json - keep as is or convert to string
            return value if isinstance(value, (str, int, float, bool, dict, list)) else str(value)
    except (ValueError, TypeError):
        # Fallback to string representation
        return str(value)


def analyze_import_impact(run, target_list):
    """Analyze what will happen when importing extracted data to a list"""
    extracted_entities = parse_extracted_data(run.extracted)
    existing_columns = {col.name: col for col in target_list.columns.all()}
    existing_rows_count = target_list.rows.count()
    
    # Analyze extracted fields
    extracted_fields = set()
    field_samples = {}
    
    for entity in extracted_entities:
        for field, value in entity.items():
            extracted_fields.add(field)
            if field not in field_samples:
                field_samples[field] = []
            if len(field_samples[field]) < 5:  # Keep up to 5 samples
                field_samples[field].append(value)
    
    # Categorize changes
    new_columns = []
    existing_columns_match = []
    conflicts = []
    
    for field in extracted_fields:
        if field in existing_columns:
            # Check for type compatibility
            detected_type = detect_column_type(field_samples[field])
            existing_col = existing_columns[field]
            if is_type_compatible(detected_type, existing_col.column_type):
                existing_columns_match.append(field)
            else:
                conflicts.append({
                    'field': field,
                    'existing_type': existing_col.column_type,
                    'detected_type': detected_type,
                    'sample_values': field_samples[field][:3]
                })
        else:
            new_columns.append({
                'name': field,
                'type': detect_column_type(field_samples[field]),
                'sample_values': field_samples[field][:3]
            })
    
    return {
        'new_rows_count': len(extracted_entities),
        'existing_rows_count': existing_rows_count,
        'new_columns': new_columns,
        'existing_columns_match': existing_columns_match,
        'conflicts': conflicts,
        'is_empty_list': existing_rows_count == 0,
        'extracted_fields_count': len(extracted_fields)
    }


@login_required
def analyze_import_to_list(request, run_pk, list_pk):
    """Analyze what will happen when importing run data to a list"""
    run = get_object_or_404(Run, pk=run_pk, user_id=request.user.id)
    
    # Handle "new list" case
    if list_pk == 'new':
        return JsonResponse({
            'success': True,
            'analysis': {
                'is_new_list': True,
                'new_rows_count': len(parse_extracted_data(run.extracted)),
                'new_columns': get_columns_from_extracted_data(run.extracted),
                'existing_columns_match': [],
                'conflicts': [],
                'is_empty_list': True,
                'extracted_fields_count': len(get_columns_from_extracted_data(run.extracted))
            }
        })
    
    target_list = get_object_or_404(UserList, pk=list_pk, user=request.user)
    analysis = analyze_import_impact(run, target_list)
    
    return JsonResponse({
        'success': True,
        'analysis': analysis
    })


def get_columns_from_extracted_data(extracted_json):
    """Extract column definitions from extracted data"""
    entities = parse_extracted_data(extracted_json)
    if not entities:
        return []
    
    # Analyze all fields across entities
    field_samples = {}
    for entity in entities:
        for field, value in entity.items():
            if field not in field_samples:
                field_samples[field] = []
            if len(field_samples[field]) < 5:
                field_samples[field].append(value)
    
    columns = []
    for field, samples in field_samples.items():
        columns.append({
            'name': field,
            'type': detect_column_type(samples),
            'sample_values': samples[:3]
        })
    
    return columns


@login_required
def add_extracted_to_list(request, run_pk, list_pk):
    """Add extracted data from a run to a list"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    run = get_object_or_404(Run, pk=run_pk, user_id=request.user.id)
    
    # Handle new list creation
    if list_pk == 'new':
        list_name = request.POST.get('list_name', '').strip()
        if not list_name:
            return JsonResponse({'success': False, 'error': 'List name is required'})
        
        target_list = UserList.objects.create(
            user=request.user,
            name=list_name,
            description=f"Created from run #{run.pk}"
        )
        
        # Create columns from extracted data
        columns = get_columns_from_extracted_data(run.extracted)
        for i, col_data in enumerate(columns):
            ListColumn.objects.create(
                user_list=target_list,
                name=col_data['name'],
                column_type=col_data['type'],
                order=i
            )
    else:
        target_list = get_object_or_404(UserList, pk=list_pk, user=request.user)
    
    try:
        result = import_extracted_to_list(run, target_list, request.user)
        return JsonResponse({
            'success': True,
            'result': result,
            'list_url': f"/lists/{target_list.pk}/"
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error importing to list: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def import_extracted_to_list(run, target_list, user):
    """Import extracted data with column creation and conflict handling"""
    analysis = analyze_import_impact(run, target_list)
    
    # Create new columns if needed (only for existing lists)
    if not analysis.get('is_new_list', False):
        for col_data in analysis['new_columns']:
            ListColumn.objects.create(
                user_list=target_list,
                name=col_data['name'],
                column_type=col_data['type'],
                order=target_list.columns.count()
            )
    
    # Refresh columns after creating new ones
    columns = {col.name: col for col in target_list.columns.all()}
    
    # Import data
    extracted_entities = parse_extracted_data(run.extracted)
    imported_count = 0
    
    for entity in extracted_entities:
        row_data = {}
        for field, value in entity.items():
            if field in columns:
                column = columns[field]
                try:
                    row_data[field] = convert_value_to_column_type(value, column.column_type)
                except ValueError as e:
                    # Handle type conversion errors
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Type conversion error for field {field}: {e}")
                    row_data[field] = str(value)  # Fallback to string
        
        ListRow.objects.create(
            user_list=target_list,
            data=row_data
        )
        imported_count += 1
    
    return {
        'imported_rows': imported_count,
        'new_columns': len(analysis['new_columns']),
        'conflicts_resolved': len(analysis['conflicts'])
    }