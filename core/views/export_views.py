import json
import csv
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from ..models import Run, UserList, ListColumn, ListRow, DataTransit, DataLandingZone


def export_list_csv(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user=request.user)
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
    list_obj = get_object_or_404(UserList, pk=pk, user=request.user)
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

    # Check if this is a raw scraped data export
    export_type = request.GET.get('type', 'extracted')

    if export_type == 'raw':
        # Export raw scraped data from DataLandingZone
        from ..models import DataLandingZone

        landing_zone_data = DataLandingZone.objects.filter(run=run, user=request.user)

        if not landing_zone_data.exists():
            return HttpResponse("No scraped data available for export", status=404)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="run_{pk}_scraped.csv"'

        writer = csv.writer(response)

        # Write headers for scraped data
        writer.writerow(['source_type', 'data'])

        # Write scraped data rows
        for entry in landing_zone_data:
            source_type = entry.source_mapping.source_type
            data_json = json.dumps(entry.data)
            writer.writerow([source_type, data_json])

        return response

    else:
        # Export extracted data from data_transit table
        # Get all data for this run from data_transit table
        transit_data = DataTransit.objects.filter(run=run).order_by('entity_id', 'attribute')

        if not transit_data.exists():
            return HttpResponse("No extracted data available for export", status=404)

        # Pivot EAV data into tabular format
        entities_dict = {}
        all_attributes = set()

        for record in transit_data:
            entity_id = record.entity_id
            attribute = record.attribute
            value = record.value

            if entity_id not in entities_dict:
                entities_dict[entity_id] = {}
            entities_dict[entity_id][attribute] = value
            all_attributes.add(attribute)

        # Convert to list of entities
        entities = []
        for entity_id, attributes in entities_dict.items():
            entity = {'entity_id': entity_id}
            entity.update(attributes)
            entities.append(entity)

        if not entities:
            return HttpResponse("No extracted data available for export", status=404)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="run_{pk}_extracted.csv"'

        writer = csv.writer(response)

        # Write headers
        headers = ['entity_id'] + sorted(list(all_attributes))
        writer.writerow(headers)

        # Write data rows
        for entity in entities:
            row = [entity.get('entity_id', '')]
            for attr in sorted(list(all_attributes)):
                value = entity.get(attr, '')
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

    # Check if this is a raw scraped data export
    export_type = request.GET.get('type', 'extracted')

    if export_type == 'raw':
        # Export raw scraped data from DataLandingZone
        from ..models import DataLandingZone

        landing_zone_data = DataLandingZone.objects.filter(run=run, user=request.user)

        if not landing_zone_data.exists():
            return JsonResponse({"error": "No scraped data available for export"}, status=404)

        # Group by source type like the API endpoint does
        grouped_data = {}
        for entry in landing_zone_data:
            source_type = entry.source_mapping.source_type
            if source_type not in grouped_data:
                grouped_data[source_type] = []
            grouped_data[source_type].append(entry.data)

        data = {
            "run_id": run.pk,
            "created_at": run.created_at.isoformat(),
            "scraped_data": grouped_data
        }

        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="run_{pk}_scraped.json"'

        return response

    else:
        # Export extracted data from data_transit table
        from ..models import DataTransit

        # Get all data for this run from data_transit table
        transit_data = DataTransit.objects.filter(run=run).order_by('entity_id', 'attribute')

        if not transit_data.exists():
            return JsonResponse({"error": "No extracted data available for export"}, status=404)

        # Pivot EAV data into entities
        entities_dict = {}
        for record in transit_data:
            entity_id = record.entity_id
            attribute = record.attribute
            value = record.value

            if entity_id not in entities_dict:
                entities_dict[entity_id] = {}
            entities_dict[entity_id][attribute] = value

        # Convert to list of entities
        entities = []
        for entity_id, attributes in entities_dict.items():
            entity = {'entity_id': entity_id}
            entity.update(attributes)
            entities.append(entity)

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