import json
import json
import logging
import requests
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import models
from .utils import geocode_location
from .models import Run, User, UserList, ListColumn, ListRow
from .forms import RunForm, SourceForm, SourceFormSet

logger = logging.getLogger(__name__)

def get_n8n_execution_status(execution_id):
    """Query n8n REST API for execution status and full data"""
    if not execution_id:
        return {'status': None, 'data': None}

    execution_api_url = settings.N8N_BASE_URL + '/api/v1/executions/' + str(execution_id) + '?includeData=true'
    headers = {'X-N8N-API-KEY': settings.N8N_API_KEY}

    try:
        response = requests.get(execution_api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {'status': data.get('status', 'unknown'), 'data': data}
        elif response.status_code == 401:
            logger.error(f"Authentication failed for execution {execution_id}")
            return {'status': 'auth_error', 'data': None}
        else:
            logger.warning(f"Failed to get execution status for {execution_id}: HTTP {response.status_code}")
            return {'status': 'unknown', 'data': None}
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout getting execution status for {execution_id}")
        return {'status': 'timeout', 'data': None}
    except Exception as e:
        logger.error(f"Exception getting execution status for {execution_id}: {str(e)}")
        return {'status': 'error', 'data': None}

def home(request):
    return render(request, 'home.html')

def test_geocode(request):
    address = request.GET.get('address', 'New York')
    lat, lng = geocode_location(address)
    return HttpResponse(f"Address: {address}<br>Lat: {lat}<br>Lng: {lng}")

def build_source_config(cleaned_data):
    """Convert Django form data to n8n configuration format"""
    source_type = cleaned_data['source_type']
    config = {}
    
    # Helper function to safely get string value and split into lines
    def get_string_list(field_name, default=''):
        value = cleaned_data.get(field_name, default)
        if isinstance(value, list):
            # If it's already a list, return it as-is
            return [str(item).strip() for item in value if str(item).strip()]
        elif isinstance(value, str):
            # If it's a string, split by lines
            return [line.strip() for line in value.splitlines() if line.strip()]
        else:
            # Convert to string and split
            return [str(value).strip() for line in str(value).splitlines() if line.strip()]
    
    if source_type.startswith('youtube-'):
        max_results = cleaned_data.get('max_results', 50)
        
        # Common fields for all YouTube source types
        config['maxResults'] = max_results
        config['maxResultsShorts'] = 0  # No shorts for testing
        config['maxResultStreams'] = 0  # No streams for testing
        
        if source_type == 'youtube-search':
            config['searchQueries'] = get_string_list('search_queries')
            config['sortingOrder'] = cleaned_data.get('sorting_order', 'relevance')
            config['dateFilter'] = cleaned_data.get('date_filter', 'month')
            config['videoType'] = cleaned_data.get('video_type', 'video')
            config['lengthFilter'] = cleaned_data.get('length_filter', 'between420')
        else:
            # YouTube channel, playlist, hashtag, video
            urls = get_string_list('profile_urls')
            config['startUrls'] = [{'url': url} for url in urls]
            # Add these fields for non-search types too (for consistency)
            config['sortingOrder'] = cleaned_data.get('sorting_order', 'date')
            config['dateFilter'] = cleaned_data.get('date_filter', '')
            config['videoType'] = cleaned_data.get('video_type', 'video')
            config['lengthFilter'] = cleaned_data.get('length_filter', '')
        
        # Complete quality filters (matching workflow pinData)
        config['qualityFilters'] = {
            'isHD': cleaned_data.get('is_hd', False),
            'hasSubtitles': cleaned_data.get('has_subtitles', False),
            'hasCC': cleaned_data.get('has_cc', False),
            'is3D': cleaned_data.get('is_3d', False),
            'isLive': cleaned_data.get('is_live', False),
            'is4K': cleaned_data.get('is_4k', False),
            'is360': cleaned_data.get('is_360', False),
            'hasLocation': cleaned_data.get('has_location', False),
            'isHDR': cleaned_data.get('is_hdr', False),
            'isVR180': cleaned_data.get('is_vr180', False),
            'isBought': cleaned_data.get('is_bought', False),
        }
        
        # Complete subtitle options (matching workflow pinData)
        config['subtitleOptions'] = {
            'language': cleaned_data.get('subtitles_language', 'en'),
            'downloadSubtitles': cleaned_data.get('download_subtitles', False),
            'saveSubsToKVS': cleaned_data.get('save_subs_to_kvs', False),
            'preferAutoGeneratedSubtitles': cleaned_data.get('prefer_auto_generated_subtitles', False),
            'subtitlesFormat': cleaned_data.get('subtitles_format', 'srt'),
        }
        
        # Also add top-level subtitle fields for Apify compatibility
        config['downloadSubtitles'] = cleaned_data.get('download_subtitles', False)
        config['saveSubsToKVS'] = cleaned_data.get('save_subs_to_kvs', False)
        config['subtitlesLanguage'] = cleaned_data.get('subtitles_language', 'en')
        config['preferAutoGeneratedSubtitles'] = cleaned_data.get('prefer_auto_generated_subtitles', False)
        config['subtitlesFormat'] = cleaned_data.get('subtitles_format', 'srt')
    
    elif source_type.startswith('instagram-'):
        if source_type == 'instagram-search':
            config['search'] = get_string_list('search_queries')
        else:
            config['directUrls'] = get_string_list('profile_urls')
        
        config['resultsType'] = cleaned_data.get('results_type', 'posts')
        config['resultsLimit'] = cleaned_data.get('max_results', 100)
        config['oldestPostDate'] = cleaned_data.get('oldest_post_date', '')
        config['relativeDateFilter'] = cleaned_data.get('relative_date_filter', '')
        config['feedType'] = cleaned_data.get('feed_type', 'posts')
    
    elif source_type.startswith('tiktok-'):
        if source_type == 'tiktok-profile':
            config['profiles'] = get_string_list('profile_urls')
        elif source_type == 'tiktok-hashtag':
            config['hashtags'] = get_string_list('hashtags')
        elif source_type == 'tiktok-search':
            config['searchQueries'] = get_string_list('search_queries')
        elif source_type == 'tiktok-video':
            config['postURLs'] = get_string_list('profile_urls')
        
        config['resultsPerPage'] = cleaned_data.get('max_results', 50)
    
    return config

def trigger_run(run):
    """Trigger multi-source n8n workflow"""
    # Parse input
    input_data = json.loads(run.input)
    sources = input_data.get('sources', [])
    days_since = input_data.get('days_since', 14)
    max_results = input_data.get('max_results', 50)
    auto_infer_columns = input_data.get('auto_infer_columns', True)
    custom_columns = input_data.get('custom_columns', [])
    extraction_prompt = input_data.get('extraction_prompt', "Extract location information, business mentions, contact details, and other relevant data from social media posts. Adapt to the specific platform and content type.")
    enable_extraction = input_data.get('enable_extraction', True)

    # Convert new sourceType format to platform format for n8n compatibility
    converted_sources = []
    for source in sources:
        source_type = source.get('sourceType', '')
        config = source.get('config', {})
        
        # Map sourceType to platform
        if source_type.startswith('youtube-'):
            platform = 'youtube'
        elif source_type.startswith('instagram-'):
            platform = 'instagram'
        elif source_type.startswith('tiktok-'):
            platform = 'tiktok'
        else:
            platform = 'instagram'  # Default fallback
        
        # Create platform-specific source object
        platform_source = {
            'platform': platform,
            'sourceType': source_type,
            'configuration': config
        }
        
        # Add legacy fields for backward compatibility
        if platform == 'instagram':
            if 'directUrls' in config:
                platform_source['directUrls'] = config['directUrls']
            elif 'search' in config:
                platform_source['search'] = config['search']
        elif platform == 'tiktok':
            if 'profiles' in config:
                platform_source['profiles'] = config['profiles']
            if 'hashtags' in config:
                platform_source['hashtags'] = config['hashtags']
            if 'searchQueries' in config:
                platform_source['searchQueries'] = config['searchQueries']
            if 'postURLs' in config:
                platform_source['postURLs'] = config['postURLs']
        elif platform == 'youtube':
            if 'startUrls' in config:
                platform_source['startUrls'] = config['startUrls']
            if 'searchQueries' in config:
                platform_source['searchQueries'] = config['searchQueries']
        
        converted_sources.append(platform_source)

    # Format payload for multi-source n8n workflow
    payload = {
        "sources": converted_sources,
        "daysSince": days_since,
        "maxResults": max_results,
        "auto_infer_columns": auto_infer_columns,
        "custom_columns": custom_columns,
        "enable_extraction": enable_extraction,
        "extraction_prompt": extraction_prompt
    }
    
    # Post to multi-source n8n webhook
    # Use test URL if available (for testing purposes)
    multi_source_url = getattr(settings, 'N8N_TEST_SCRAPING_URL', settings.N8N_BASE_URL + '/webhook/multi-source-scrape')
    
    try:
        logger.info(f"Triggering multi-source n8n workflow for run {run.pk} at {multi_source_url}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(multi_source_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            # Parse execution_id from response
            response_data = response.json()
            run.n8n_execution_id = response_data.get('execution_id')
            run.save()
            logger.info(f"Run {run.pk} started with execution {run.n8n_execution_id}")
        else:
            logger.error(f"Failed to start run {run.pk}: HTTP {response.status_code} - {response.text}")
            # Try fallback to legacy webhook if multi-source fails
            try_legacy_fallback(run, input_data)
    except Exception as e:
        logger.error(f"Exception while triggering run {run.pk}: {str(e)}")
        # Try fallback to legacy webhook
        try_legacy_fallback(run, input_data)

def try_legacy_fallback(run, input_data):
    """Fallback to legacy single-source workflow if multi-source fails"""
    try:
        logger.info(f"Attempting fallback to legacy workflow for run {run.pk}")
        
        # Extract first source for fallback
        sources = input_data.get('sources', [])
        if not sources:
            logger.error("No sources available for fallback")
            return
            
        first_source = sources[0]
        source_type = first_source.get('sourceType', '')
        config = first_source.get('config', {})
        
        # Map sourceType to platform
        if source_type.startswith('youtube-'):
            platform = 'youtube'
        elif source_type.startswith('instagram-'):
            platform = 'instagram'
        elif source_type.startswith('tiktok-'):
            platform = 'tiktok'
        else:
            platform = 'instagram'  # Default fallback
        
        # Extract URLs based on source type and config
        profiles = []
        if platform == 'instagram':
            profiles = config.get('directUrls', [])
        elif platform == 'tiktok':
            profiles = config.get('profiles', [])
            # For TikTok video, use postURLs
            if not profiles and 'postURLs' in config:
                profiles = config.get('postURLs', [])
            # For TikTok search, use search queries as profiles for legacy compatibility
            if not profiles and 'searchQueries' in config:
                profiles = config.get('searchQueries', [])
        elif platform == 'youtube':
            # For YouTube, try different URL types
            if 'startUrls' in config:
                profiles = [url.get('url', '') if isinstance(url, dict) else url for url in config['startUrls']]
            elif 'searchQueries' in config:
                # For search, use search queries as profiles for legacy compatibility
                profiles = config.get('searchQueries', [])
        
        if not profiles:
            logger.error(f"No profiles/URLs found for {platform} source in legacy fallback")
            return
        
        days_since = input_data.get('days_since', 14)
        max_results = input_data.get('max_results', 50)
        extraction_prompt = input_data.get('extraction_prompt', "Extract location information, business mentions, and contact details from social media posts.")
        
        # Format legacy payload
        n8n_profiles = []
        for url in profiles:
            if url and url.strip():
                n8n_profiles.append({
                    "url": url.strip(),
                    "type": platform
                })
        
        if not n8n_profiles:
            logger.error("No valid profiles to process in legacy fallback")
            return
        
        legacy_payload = {
            "user_id": run.user_id,
            "tier": "premium",
            "days_since": days_since,
            "max_results": max_results,
            "extraction_prompt": extraction_prompt,
            "profiles": n8n_profiles
        }
        
        # Post to legacy n8n webhook
        webscrape_url = settings.N8N_WEBSCRAPE_URL
        response = requests.post(webscrape_url, json=legacy_payload, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            run.n8n_execution_id = response_data.get('execution_id')
            run.save()
            logger.info(f"Run {run.pk} started with legacy execution {run.n8n_execution_id}")
        else:
            logger.error(f"Legacy fallback also failed for run {run.pk}: HTTP {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Exception in legacy fallback for run {run.pk}: {str(e)}")

def run_create(request):
    if request.method == 'POST':
        source_formset = SourceFormSet(request.POST, prefix='form')
        
        # Process sources from formset first
        sources = []
        if source_formset.is_valid():
            for source_form in source_formset:
                if source_form.is_valid() and source_form.cleaned_data.get('source_type'):
                    source_config = build_source_config(source_form.cleaned_data)
                    sources.append({
                        "sourceType": source_form.cleaned_data['source_type'],
                        "config": source_config
                    })
        
        # Update POST data with processed sources
        post_data = request.POST.copy()
        post_data['sources'] = json.dumps(sources)
        
        form = RunForm(post_data)
        
        if source_formset.is_valid() and form.is_valid():
            # Create run with processed sources (already in form.cleaned_data['sources'])
            run = form.save(commit=False)
            run.user_id = 1  # Dummy user_id for development
            run.input = json.dumps({
                'sources': sources,
                'days_since': form.cleaned_data['days_since'],
                'max_results': form.cleaned_data['max_results'],
                'auto_infer_columns': form.cleaned_data['auto_infer_columns'],
                'custom_columns': form.cleaned_data['custom_columns'],
                'extraction_prompt': form.cleaned_data['extraction_prompt']
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

def run_list(request):
    # For now, filter by dummy user_id=1
    runs = Run.objects.filter(user_id=1).order_by('-created_at')

    # Add execution status to each run
    runs_with_status = []
    for run in runs:
        execution_info = get_n8n_execution_status(run.n8n_execution_id)
        runs_with_status.append({
            'run': run,
            'status': execution_info['status']
        })

    return render(request, 'core/run_list.html', {'runs_with_status': runs_with_status})

def run_detail(request, pk):
    run = get_object_or_404(Run, pk=pk)
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

# User List Management Views
def list_list(request):
    # Dummy user for now
    user_id = 1
    lists = UserList.objects.filter(user_id=user_id).order_by('-created_at')
    return render(request, 'core/list_list.html', {'lists': lists})

def list_detail(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)  # Dummy user
    columns = list_obj.columns.all().order_by('order')
    rows = list_obj.rows.all()

    # Serialize data for Alpine.js table editor
    columns_data = []
    for column in columns:
        columns_data.append({
            'id': column.pk,
            'name': column.name,
            'type': column.column_type,
            'options': column.options or {}
        })

    rows_data = []
    for row in rows:
        rows_data.append({
            'id': row.pk,
            'data': row.data or {}
        })

    return render(request, 'core/list_detail.html', {
        'list': list_obj,
        'columns': columns,
        'rows': rows,
        'columns_json': json.dumps(columns_data),
        'rows_json': json.dumps(rows_data)
    })

def list_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if name:
            # Get or create the dummy user
            user, created = User.objects.get_or_create(
                id=1,
                defaults={'username': 'dev', 'email': 'dev@example.com'}
            )

            # Create the list
            user_list = UserList.objects.create(
                user=user,
                name=name,
                description=description
            )

            # Create default columns
            ListColumn.objects.create(
                user_list=user_list,
                name='source',
                column_type='text',
                description='Where this data came from',
                order=0
            )
            ListColumn.objects.create(
                user_list=user_list,
                name='last_updated',
                column_type='date',
                description='When this entry was last updated',
                order=1
            )

            messages.success(request, f'List "{name}" created successfully!')
            return redirect('list_detail', pk=user_list.pk)
        else:
            messages.error(request, 'Please provide a list name.')
    return render(request, 'core/list_create.html')

def list_column_create(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
    if request.method == 'POST':
        name = request.POST.get('name')
        column_type = request.POST.get('column_type')
        required = request.POST.get('required') == 'on'
        order = list_obj.columns.count()

# Handle options for select/multi_select
        options = None
        if column_type in ['select', 'multi_select']:
            if column_type == 'select':
                options = ['Active', 'Pending', 'Completed', 'Archived']
            elif column_type == 'multi_select':
                options = []

        if name and column_type:
            new_column = ListColumn.objects.create(
                user_list=list_obj,
                name=name,
                column_type=column_type,
                required=required,
                order=order,
                options=options
            )

            # Check if this is an HTMX request
            if request.headers.get('HX-Request'):
                # Re-render the table editor with updated data
                columns = list_obj.columns.all().order_by('order')
                rows = list_obj.rows.all()

                # Serialize data for Alpine.js table editor
                columns_data = []
                for column in columns:
                    columns_data.append({
                        'id': column.pk,
                        'name': column.name,
                        'type': column.column_type,
                        'options': column.options or {}
                    })

                rows_data = []
                for row in rows:
                    rows_data.append({
                        'id': row.pk,
                        'data': row.data or {}
                    })

                context = {
                    'list': list_obj,
                    'columns': columns,
                    'rows': rows,
                    'columns_json': columns_data,
                    'rows_json': rows_data
                }

                from django.template.loader import render_to_string
                html = render_to_string('snippets/_table_editor.html', context, request)
                return HttpResponse(html)

# For non-HTMX requests, return the new column data
            column_data = {
                'id': new_column.pk,
                'name': new_column.name,
                'type': new_column.column_type,
                'options': new_column.options or {}
            }
            
            messages.success(request, 'Column added successfully!')
            return JsonResponse({'success': True, 'column': column_data})
        
        return JsonResponse({'success': False})

def list_row_create(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
    columns = list_obj.columns.all().order_by('order')

    if request.method == 'POST':
        row_data = {}
        for column in columns:
            value = request.POST.get(f'column_{column.pk}')
            if column.column_type == 'number' and value:
                try:
                    row_data[column.name] = float(value)
                except ValueError:
                    row_data[column.name] = value
            elif column.column_type == 'boolean':
                row_data[column.name] = value == 'on'
            elif column.column_type == 'select' and value:
                row_data[column.name] = value
            elif column.column_type == 'multi_select' and value:
                # Handle multi-select as comma-separated values
                tags = [tag.strip() for tag in value.split(',') if tag.strip()]
                row_data[column.name] = tags if tags else None
            elif column.column_type == 'url' and value:
                row_data[column.name] = value
            elif column.column_type == 'json' and value:
                try:
                    row_data[column.name] = json.loads(value)
                except json.JSONDecodeError:
                    row_data[column.name] = value
            else:
                row_data[column.name] = value or None

        # Handle insert_after parameter for positioning
        insert_after = request.POST.get('insert_after')
        if insert_after:
            try:
                after_row = ListRow.objects.get(pk=int(insert_after), user_list=list_obj)
                # For now, just create at the end. Could implement proper ordering later
                ListRow.objects.create(
                    user_list=list_obj,
                    data=row_data
                )
            except (ListRow.DoesNotExist, ValueError):
                ListRow.objects.create(
                    user_list=list_obj,
                    data=row_data
                )
        else:
            ListRow.objects.create(
                user_list=list_obj,
                data=row_data
            )

        # Check if this is an HTMX request
        if request.headers.get('HX-Request'):
            # Re-render the table editor with updated data
            columns = list_obj.columns.all().order_by('order')
            rows = list_obj.rows.all()

            # Serialize data for Alpine.js table editor
            columns_data = []
            for column in columns:
                columns_data.append({
                    'id': column.pk,
                    'name': column.name,
                    'type': column.column_type,
                    'options': column.options or {}
                })

            rows_data = []
            for row in rows:
                # Ensure data is a dict and handle None values properly
                row_data = row.data or {}
                # Convert any None values to None (they should already be None, but ensure consistency)
                cleaned_data = {k: v for k, v in row_data.items()}
                rows_data.append({
                    'id': row.pk,
                    'data': cleaned_data
                })

            context = {
                'list': list_obj,
                'columns': columns,
                'rows': rows,
                'columns_json': json.dumps(columns_data),
                'rows_json': json.dumps(rows_data)
            }

            from django.template.loader import render_to_string
            html = render_to_string('snippets/_table_editor.html', context, request)
            return HttpResponse(html)

        messages.success(request, 'Row added successfully!')
        return redirect('list_detail', pk=pk)

    return render(request, 'core/list_row_create.html', {
        'list': list_obj,
        'columns': columns
    })

def export_list_csv(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
    columns = list_obj.columns.all().order_by('order')
    rows = list_obj.rows.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{list_obj.name}.csv"'

    writer = csv.writer(response)
    # Write header
    header = ['ID'] + [col.name for col in columns] + ['Created At']
    writer.writerow(header)

    for row in rows:
        row_data = [row.pk]
        for col in columns:
            value = row.data.get(col.name, '')
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            row_data.append(str(value))
        row_data.append(row.created_at.isoformat())
        writer.writerow(row_data)

    return response

def export_list_json(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
    columns = list_obj.columns.all().order_by('order')
    rows = list_obj.rows.all()

    data = {
        'list': {
            'id': list_obj.pk,
            'name': list_obj.name,
            'description': list_obj.description,
            'created_at': list_obj.created_at.isoformat()
        },
        'columns': [
            {
                'name': col.name,
                'type': col.column_type,
                'required': col.required
            } for col in columns
        ],
        'rows': [
            {
                'id': row.pk,
                'data': row.data,
                'created_at': row.created_at.isoformat(),
                'updated_at': row.updated_at.isoformat()
            } for row in rows
        ]
    }

    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{list_obj.name}.json"'

    return response

# AJAX views for inline editing
def update_cell(request, pk):
    if request.method == 'POST':
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        row_id = request.POST.get('row_id')
        column = request.POST.get('column')
        value = request.POST.get('value')
        cell_type = request.POST.get('type')

        try:
            row = ListRow.objects.get(pk=row_id, user_list=list_obj)
            row_data = row.data.copy() if row.data else {}

            # Convert value based on type
            if cell_type == 'boolean':
                row_data[column] = value.lower() == 'true'
            elif cell_type == 'number' and value:
                try:
                    row_data[column] = float(value)
                except ValueError:
                    row_data[column] = value
            elif cell_type == 'date' and value:
                row_data[column] = value
            else:
                row_data[column] = value if value else None

            row.data = row_data
            row.save()

            return JsonResponse({'success': True})
        except ListRow.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Row not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def delete_row(request, pk):
    if request.method == 'POST':
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        row_id = request.POST.get('row_id')

        try:
            # Convert row_id to int if it's a string
            if isinstance(row_id, str):
                row_id = int(row_id)
            row = ListRow.objects.get(pk=row_id, user_list=list_obj)
            row.delete()
            return JsonResponse({'success': True})
        except (ListRow.DoesNotExist, ValueError):
            return JsonResponse({'success': False, 'error': 'Row not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def add_blank_row(request, pk):
    """Add a blank row to the table via HTMX"""
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
    columns = list_obj.columns.all().order_by('order')

    if request.method == 'POST':
        # Get insert_after parameter if provided
        insert_after_id = request.POST.get('insert_after')
        
        # Create row with empty data for all columns
        row_data = {}
        for column in columns:
            if column.column_type == 'boolean':
                row_data[column.name] = False
            elif column.column_type == 'number':
                row_data[column.name] = None
            elif column.column_type == 'select':
                row_data[column.name] = None
            elif column.column_type == 'multi_select':
                row_data[column.name] = []
            else:
                row_data[column.name] = None

        # Create the new row
        new_row = ListRow.objects.create(
            user_list=list_obj,
            data=row_data
        )

        # If insert_after is specified, handle positioning
        if insert_after_id:
            try:
                insert_after_row = ListRow.objects.get(pk=insert_after_id, user_list=list_obj)
                # Get all rows and find the position
                all_rows = list_obj.rows.all().order_by('created_at')
                insert_after_index = list(all_rows).index(insert_after_row)
                
                # Return position info for frontend
                row_json = {
                    'id': new_row.pk,
                    'data': row_data,
                    'insert_after_index': insert_after_index
                }
            except ListRow.DoesNotExist:
                # Fallback if insert_after row not found
                row_json = {
                    'id': new_row.pk,
                    'data': row_data
                }
        else:
            # Regular add at end
            row_json = {
                'id': new_row.pk,
                'data': row_data
            }
            
        return JsonResponse({'success': True, 'row': row_json})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@require_http_methods(["POST"])
def table_save(request, pk):
    """Batch save table data from HTMX/Alpine.js table editor"""
    try:
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        data = json.loads(request.POST.get('data', '{}'))

        logger.info(f"Table save request for list {pk} with data: {data}")

        updated_rows = 0

        # Process each row's changes
        for row_id, changes in data.items():
            try:
                row = ListRow.objects.get(pk=int(row_id), user_list=list_obj)
                row_data = row.data.copy() if row.data else {}

                # Apply changes to row data
                for column_id, value in changes.items():
                    # Find column by ID to get column name
                    column = list_obj.columns.filter(pk=int(column_id)).first()
                    if column:
                        # Convert value based on column type
                        if column.column_type == 'boolean':
                            row_data[column.name] = value.lower() == 'true' if isinstance(value, str) else bool(value)
                        elif column.column_type == 'number' and value:
                            try:
                                row_data[column.name] = float(value)
                            except (ValueError, TypeError):
                                row_data[column.name] = value
                        elif column.column_type == 'date' and value:
                            row_data[column.name] = value
                        else:
                            row_data[column.name] = value if value else None

                row.data = row_data
                row.save()
                updated_rows += 1
                logger.info(f"Updated row {row_id} with changes: {changes}")

            except ListRow.DoesNotExist:
                logger.warning(f"Row {row_id} does not exist")
                continue  # Skip rows that don't exist

        logger.info(f"Successfully updated {updated_rows} rows")

        # Re-render the table editor with updated data
        columns = list_obj.columns.all().order_by('order')
        rows = list_obj.rows.all()

        # Serialize data for Alpine.js table editor
        columns_data = []
        for column in columns:
            columns_data.append({
                'id': column.pk,
                'name': column.name,
                'type': column.column_type,
                'options': column.options or {}
            })

        rows_data = []
        for row in rows:
            rows_data.append({
                'id': row.pk,
                'data': row.data or {}
            })

        context = {
            'list': list_obj,
            'columns': columns,
            'rows': rows,
            'columns_json': columns_data,
            'rows_json': rows_data
        }

        from django.template.loader import render_to_string
        html = render_to_string('snippets/_table_editor.html', context, request)
        logger.info(f"Rendered HTML response, length: {len(html)}")
        return HttpResponse(html)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return HttpResponse('<div class="text-red-600">Error: Invalid data format</div>', status=400)
    except Exception as e:
        logger.error(f"Error saving table data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return HttpResponse('<div class="text-red-600">Error: Failed to save data</div>', status=500)

def update_column(request, pk, column_id):
    if request.method == 'POST':
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        column = get_object_or_404(ListColumn, pk=column_id, user_list=list_obj)

        # Update name
        if 'name' in request.POST:
            name = request.POST.get('name').strip()
            if not name:
                return JsonResponse({'success': False, 'error': 'Column name cannot be empty'})
            column.name = name

        # Update column type
        if 'column_type' in request.POST:
            new_type = request.POST.get('column_type')
            if new_type not in dict(ListColumn.COLUMN_TYPES):
                return JsonResponse({'success': False, 'error': 'Invalid column type'})

            # Check if type change would break existing data
            if column.column_type != new_type and list_obj.rows.exists():
                # For now, allow type changes but warn user
                pass

            column.column_type = new_type

            # Set default options for select types
            if new_type == 'select' and not column.options:
                column.options = ['Active', 'Pending', 'Completed', 'Archived']
            elif new_type == 'multi_select' and not column.options:
                column.options = []

        # Update description
        if 'description' in request.POST:
            column.description = request.POST.get('description', '').strip()

# Update required
        if 'required' in request.POST:
            column.required = request.POST.get('required').lower() == 'true'

        column.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@require_http_methods(["POST"])
def validate_column_type_change(request, pk, column_id):
    """Validate if column type change is safe"""
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
    column = get_object_or_404(ListColumn, pk=column_id, user_list=list_obj)
    new_type = request.POST.get('column_type')
    
    if not new_type or new_type not in dict(ListColumn.COLUMN_TYPES):
        return JsonResponse({'success': False, 'error': 'Invalid column type'})
    
    # Get existing data
    rows = list_obj.rows.all()
    existing_data = [row.data.get(column.name) for row in rows if row.data.get(column.name) is not None]
    
    # Remove empty values
    non_empty_data = [str(val).strip() for val in existing_data if str(val).strip()]
    
    if not non_empty_data:
        return JsonResponse({
            'success': True, 
            'allowed': True, 
            'message': 'Column is empty - any type allowed',
            'sample_conflicts': []
        })
    
    # Validate compatibility based on current type
    validation = validate_type_compatibility(non_empty_data, column.column_type, new_type)
    
    return JsonResponse({
        'success': True,
        'allowed': validation['allowed'],
        'message': validation['message'],
        'sample_conflicts': validation.get('sample_conflicts', [])
    })

def validate_type_compatibility(data, current_type, new_type):
    """Check if data can be safely converted to new type"""
    
    # Define compatibility rules
    def is_number(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def is_date(value):
        try:
            from datetime import datetime
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    datetime.strptime(value, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def is_boolean(value):
        return str(value).lower() in ['true', 'false', '1', '0', 'yes', 'no']
    
    def is_url(value):
        try:
            from urllib.parse import urlparse
            result = urlparse(value)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    # Check for incompatible data
    conflicts = []
    
    # If current type is number, check for non-numeric values
    if current_type == 'number':
        for value in data:
            if not is_number(value):
                conflicts.append(value)
    
    # If current type is date, check for non-date values
    elif current_type == 'date':
        for value in data:
            if not is_date(value):
                conflicts.append(value)
    
    # If current type is boolean, check for non-boolean values
    elif current_type == 'boolean':
        for value in data:
            if not is_boolean(value):
                conflicts.append(value)
    
    # If current type is url, check for non-url values
    elif current_type == 'url':
        for value in data:
            if not is_url(value) and value.strip():  # Allow empty strings
                conflicts.append(value)
    
    if conflicts:
        return {
            'allowed': False,
            'message': f'Cannot change to {new_type}: {len(conflicts)} values would be incompatible',
            'sample_conflicts': conflicts[:3]  # Show first 3 conflicts
        }
    
    return {'allowed': True, 'message': 'Type change is safe'}

def delete_column(request, pk, column_id):
    if request.method == 'POST':
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        column = get_object_or_404(ListColumn, pk=column_id, user_list=list_obj)

        # Check if this is the last column
        if list_obj.columns.count() <= 1:
            return JsonResponse({'success': False, 'error': 'Cannot delete the last column'})

        column.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def delete_list(request, pk):
    if request.method == 'POST':
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        confirmation = request.POST.get('confirmation', '').strip()

        # Check confirmation matches list name
        if confirmation != list_obj.name:
            return JsonResponse({'success': False, 'error': 'Confirmation text does not match list name'})

        # Delete all related data
        list_obj.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def export_run_csv(request, pk):
    run = get_object_or_404(Run, pk=pk)
    entities = []

    # Extract entities from various possible data structures
    if run.extracted:
        if isinstance(run.extracted, dict):
            if 'result' in run.extracted and isinstance(run.extracted['result'], list):
                entities = run.extracted['result']
            elif 'results' in run.extracted and isinstance(run.extracted['results'], list):
                entities = run.extracted['results']
            elif 'output' in run.extracted and isinstance(run.extracted['output'], dict):
                output = run.extracted['output']
                if 'results' in output and isinstance(output['results'], list):
                    entities = output['results']
                elif 'result' in output and isinstance(output['result'], list):
                    entities = output['result']
        elif isinstance(run.extracted, list):
            entities = run.extracted

    # Fallback to legacy output
    if not entities and run.output and isinstance(run.output, list):
        entities = run.output

    if not entities:
        return HttpResponse("No extracted data available for export", status=404)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="run_{pk}_extracted.csv"'

    writer = csv.writer(response)

    # Write headers from first entity
    if entities:
        headers = list(entities[0].keys())
        writer.writerow(headers)

        # Write data rows
        for entity in entities:
            row = []
            for header in headers:
                value = entity.get(header, '')
                if isinstance(value, list):
                    row.append(', '.join(str(v) for v in value))
                elif isinstance(value, dict):
                    row.append(json.dumps(value))
                else:
                    row.append(str(value))
            writer.writerow(row)

    return response

def export_run_json(request, pk):
    run = get_object_or_404(Run, pk=pk)
    entities = []

    # Extract entities from various possible data structures
    if run.extracted:
        if isinstance(run.extracted, dict):
            if 'result' in run.extracted and isinstance(run.extracted['result'], list):
                entities = run.extracted['result']
            elif 'results' in run.extracted and isinstance(run.extracted['results'], list):
                entities = run.extracted['results']
            elif 'output' in run.extracted and isinstance(run.extracted['output'], dict):
                output = run.extracted['output']
                if 'results' in output and isinstance(output['results'], list):
                    entities = output['results']
                elif 'result' in output and isinstance(output['result'], list):
                    entities = output['result']
        elif isinstance(run.extracted, list):
            entities = run.extracted

    # Fallback to legacy output
    if not entities and run.output and isinstance(run.output, list):
        entities = run.output

    if not entities:
        return JsonResponse({"error": "No extracted data available for export"}, status=404)

    data = {
        "run_id": run.pk,
        "created_at": run.created_at.isoformat(),
        "entities": entities
    }

    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="run_{pk}_extracted.json"'

    return response

# Create your views here.
