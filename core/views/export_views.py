import json
import csv
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from ..models import Run, UserList, ListColumn, ListRow


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


def export_run_scraped_json(request, pk):
    run = get_object_or_404(Run, pk=pk)
    
    if not run.scraped:
        return JsonResponse({"error": "No scraped data available for export"}, status=404)
    
    data = {
        "run_id": run.pk,
        "created_at": run.created_at.isoformat(),
        "scraped_data": run.scraped
    }
    
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="run_{pk}_scraped.json"'
    
    return response