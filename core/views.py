import json
import logging
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from .utils import geocode_location
from .models import Run
from .forms import RunForm

logger = logging.getLogger(__name__)

def get_n8n_execution_status(execution_id):
    """Query n8n REST API for execution status"""
    if not execution_id:
        return None

    execution_api_url = settings.N8N_BASE_URL + '/api/v1/executions/' + str(execution_id) + '?includeData=true'
    headers = {'X-N8N-API-KEY': settings.N8N_API_KEY}

    try:
        response = requests.get(execution_api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('status', 'unknown')
        elif response.status_code == 401:
            logger.error(f"Authentication failed for execution {execution_id}")
            return 'auth_error'
        else:
            logger.warning(f"Failed to get execution status for {execution_id}: HTTP {response.status_code}")
            return 'unknown'
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout getting execution status for {execution_id}")
        return 'timeout'
    except Exception as e:
        logger.error(f"Exception getting execution status for {execution_id}: {str(e)}")
        return 'error'

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
            "days_since": days_since,
            "type": "instagram",
            "max_results": max_results,
            # "include_comments": include_comments,  # Hidden for now
            # "include_stories": include_stories,    # Hidden for now
            "extraction_prompt": extraction_prompt
        })
    payload = {
        "user_id": run.user_id,
        "tier": "premium",  # stub
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
        status = get_n8n_execution_status(run.n8n_execution_id)
        runs_with_status.append({
            'run': run,
            'status': status
        })

    return render(request, 'core/run_list.html', {'runs_with_status': runs_with_status})

def run_detail(request, pk):
    run = get_object_or_404(Run, pk=pk)
    status = get_n8n_execution_status(run.n8n_execution_id)
    return render(request, 'core/run_detail.html', {'run': run, 'execution_status': status})

def run_by_n8n(request, n8n_execution_id):
    run = get_object_or_404(Run, n8n_execution_id=n8n_execution_id)
    status = get_n8n_execution_status(run.n8n_execution_id)
    return render(request, 'core/run_detail.html', {'run': run, 'execution_status': status})

# Create your views here.
