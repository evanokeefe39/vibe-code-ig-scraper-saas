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

    # Prepare input data for JavaScript
    input_json = json.dumps(run.input) if isinstance(run.input, dict) else (run.input if isinstance(run.input, str) else 'null')

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
        'input_json': input_json,
        'run_data': run_data,
        'run_data_json': run_data_json,
        'run_scraped_json': json.dumps(run.scraped) if run.scraped else None
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
                name='Source',
                column_type='text',
                description='Where this data came from',
                order=0
            )
            ListColumn.objects.create(
                user_list=user_list,
                name='Created At',
                column_type='date',
                description='When this entry was created',
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
            ListColumn.objects.create(
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

            messages.success(request, 'Column added successfully!')
            return JsonResponse({'success': True})
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
            row = ListRow.objects.get(pk=row_id, user_list=list_obj)
            row.delete()
            return JsonResponse({'success': True})
        except ListRow.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Row not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def add_blank_row(request, pk):
    """Add a blank row to the table via HTMX"""
    list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
    columns = list_obj.columns.all().order_by('order')

    if request.method == 'POST':
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

        # Return JSON data for the new row
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
