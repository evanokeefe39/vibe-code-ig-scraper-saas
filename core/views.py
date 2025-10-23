import json
import logging
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from .utils import geocode_location
from .models import Run, CuratedList, CuratedItem
from .forms import RunForm

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

def trigger_run(run):
    # Parse input
    input_data = json.loads(run.input)
    profiles = input_data.get('profiles', [])
    days_since = input_data.get('days_since', 14)
    max_results = input_data.get('max_results', 50)
    # include_comments = input_data.get('include_comments', True)  # Hidden for now
    # include_stories = input_data.get('include_stories', False)   # Hidden for now
    extraction_prompt = input_data.get('extraction_prompt', "Extract location information, business mentions, and contact details from social media posts.")

    # Format payload for n8n
    n8n_profiles = []
    for url in profiles:
        n8n_profiles.append({
            "url": url,
            "type": "instagram"
        })
    payload = {
        "user_id": run.user_id,
        "tier": "premium",  # stub
        "days_since": days_since,
        "max_results": max_results,
        "extraction_prompt": extraction_prompt,
        "profiles": n8n_profiles
    }
    # Post to n8n webhook
    webscrape_url = settings.N8N_WEBSCRAPE_URL
    try:
        logger.info(f"Triggering n8n workflow for run {run.pk} at {webscrape_url}")
        response = requests.post(webscrape_url, json=payload, timeout=10)
        if response.status_code == 200:
            # Parse execution_id from response
            response_data = response.json()
            run.n8n_execution_id = response_data.get('execution_id')
            run.save()
            logger.info(f"Run {run.pk} started with execution {run.n8n_execution_id}")
        else:
            logger.error(f"Failed to start run {run.pk}: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Exception while triggering run {run.pk}: {str(e)}")

def run_create(request):
    if request.method == 'POST':
        form = RunForm(request.POST)
        if form.is_valid():
            run = form.save(commit=False)
            run.user_id = 1  # Dummy user_id for development
            run.save()
            trigger_run(run)
            messages.success(request, 'Run started successfully!')
            return redirect('run_detail', pk=run.pk)
    else:
        form = RunForm()
    return render(request, 'core/run_create.html', {'form': form})

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
    run_output_json = json.dumps(run.output) if run.output else 'null'
    return render(request, 'core/run_detail.html', {
        'run': run,
        'execution_status': execution_info['status'],
        'execution_data': execution_info['data'],
        'execution_data_json': execution_data_json,
        'run_output_json': run_output_json
    })

def run_by_n8n(request, n8n_execution_id):
    run = get_object_or_404(Run, n8n_execution_id=n8n_execution_id)
    execution_info = get_n8n_execution_status(run.n8n_execution_id)
    execution_data_json = json.dumps(execution_info['data'])
    run_output_json = json.dumps(run.output) if run.output else 'null'
    return render(request, 'core/run_detail.html', {
        'run': run,
        'execution_status': execution_info['status'],
        'execution_data': execution_info['data'],
        'execution_data_json': execution_data_json,
        'run_output_json': run_output_json
    })

def run_status_api(request, pk):
    run = get_object_or_404(Run, pk=pk)
    execution_info = get_n8n_execution_status(run.n8n_execution_id)
    return JsonResponse({
        'status': execution_info['status'],
        'data': execution_info['data']
    })

# Curation views
def entity_list(request):
    # For now, dummy user_id=1
    user_id = 1
    runs = Run.objects.filter(user_id=user_id, output__isnull=False)

    entities = []
    for run in runs:
        if isinstance(run.output, list):
            for entity in run.output:
                entities.append({
                    'data': entity,
                    'run_id': run.pk,
                    'run_created': run.created_at
                })

    # Get user's collections for the dropdown
    collections = CuratedList.objects.filter(user_id=user_id)

    return render(request, 'core/entity_list.html', {
        'entities': entities,
        'collections': collections
    })

def collection_list(request):
    # Dummy user
    user_id = 1
    collections = CuratedList.objects.filter(user_id=user_id).order_by('-created_at')
    return render(request, 'core/collection_list.html', {'collections': collections})

def collection_detail(request, pk):
    collection = get_object_or_404(CuratedList, pk=pk, user_id=1)  # Dummy user
    items = CuratedItem.objects.filter(curated_list=collection).order_by('-created_at')
    return render(request, 'core/collection_detail.html', {
        'collection': collection,
        'items': items
    })

def collection_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            CuratedList.objects.create(
                user_id=1,  # Dummy
                name=name,
                description=description
            )
            messages.success(request, 'Collection created successfully!')
            return redirect('collection_list')
    return render(request, 'core/collection_create.html')

# AJAX view to add entity to collection
def add_to_collection(request):
    if request.method == 'POST':
        collection_id = request.POST.get('collection_id')
        run_id = request.POST.get('run_id')
        entity_index = int(request.POST.get('entity_index', 0))

        try:
            collection = CuratedList.objects.get(pk=collection_id, user_id=1)
            run = Run.objects.get(pk=run_id, user_id=1)
            if isinstance(run.output, list) and 0 <= entity_index < len(run.output):
                entity_data = run.output[entity_index]
                CuratedItem.objects.create(
                    user_id=1,
                    curated_list=collection,
                    source_run=run,
                    entity_data=entity_data
                )
                return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error adding to collection: {e}")
    return JsonResponse({'success': False})

# Create your views here.
