import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Run
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