import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from ..models import User, UserList, ListColumn, ListRow

logger = logging.getLogger(__name__)


@login_required
def list_list(request):
    lists = UserList.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/list_list.html', {'lists': lists})


@login_required
def list_detail(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user=request.user)
    columns = list_obj.columns.all().order_by('order')
    rows = list_obj.rows.all()

    # Check if user wants AG-Grid version (default to AG-Grid, legacy for old table)
    use_ag_grid = request.GET.get('grid', 'ag') != 'legacy'

    # Serialize data for AG-Grid
    if use_ag_grid:
        columns_data = []
        for column in columns:
            columns_data.append({
                'id': column.pk,
                'name': column.name,
                'field': column.field,
                'column_type': column.column_type,
                'options': column.options or {}
            })

        rows_data = []
        for row in rows:
            row_data = {'id': row.pk}
            # Flatten data for AG-Grid
            if row.data:
                for column in columns:
                    field_name = column.field
                    row_data[field_name] = row.data.get(field_name, '')
            else:
                for column in columns:
                    row_data[column.field] = ''

            rows_data.append(row_data)

        return render(request, 'core/list_detail_ag_grid.html', {
            'list': list_obj,
            'columns': columns,
            'rows': rows,
            'columns_json': json.dumps(columns_data),
            'rows_json': json.dumps(rows_data)
        })
    else:
        # Legacy Alpine.js table editor
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


@login_required
def list_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if name:
            # Create the list for the authenticated user
            user_list = UserList.objects.create(
                user=request.user,
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


@login_required
def list_column_create(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user=request.user)
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


@login_required
def list_row_create(request, pk):
    list_obj = get_object_or_404(UserList, pk=pk, user=request.user)
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

            html = render_to_string('snippets/_table_editor.html', context, request)
            return HttpResponse(html)

        messages.success(request, 'Row added successfully!')
        return redirect('list_detail', pk=pk)

    return render(request, 'core/list_row_create.html', {
        'list': list_obj,
        'columns': columns
    })


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

        # Create new row
        new_row = ListRow.objects.create(
            user_list=list_obj,
            data=row_data
        )

        # If insert_after is specified, handle positioning
        if insert_after_id:
            try:
                insert_after_row = ListRow.objects.get(pk=insert_after_id, user_list=list_obj)
                # Get all rows and find position
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

        import logging
        logger = logging.getLogger(__name__)
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
        
        # For form submission, redirect after deletion
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Delete all related data
            list_obj.delete()
            messages.success(request, f'List "{list_obj.name}" has been deleted successfully.')
            return redirect('list_list')
        
        # For AJAX requests, check confirmation
        confirmation = request.POST.get('confirmation', '').strip()
        if confirmation != list_obj.name:
            return JsonResponse({'success': False, 'error': 'Confirmation text does not match list name'})

        # Delete all related data
        list_obj.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# AG-Grid specific views
@require_http_methods(["POST"])
def delete_selected_rows(request, pk):
    """Delete multiple rows selected in AG-Grid"""
    try:
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        data = json.loads(request.body)
        row_ids = data.get('ids', [])
        
        if not row_ids:
            return JsonResponse({'success': False, 'error': 'No rows selected'})
        
        # Delete rows
        deleted_count = ListRow.objects.filter(
            pk__in=row_ids,
            user_list=list_obj
        ).delete()[0]
        
        return JsonResponse({
            'success': True, 
            'deleted_count': deleted_count,
            'message': f'Deleted {deleted_count} row(s)'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error deleting selected rows: {e}")
        return JsonResponse({'success': False, 'error': 'Server error'})


@require_http_methods(["POST"])
def add_column_ag_grid(request, pk):
    """Add new column for AG-Grid table"""
    try:
        list_obj = get_object_or_404(UserList, pk=pk, user__id=1)
        data = json.loads(request.body)
        
        name = data.get('name', '').strip()
        column_type = data.get('type', 'text')
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Column name is required'})
        
        if column_type not in dict(ListColumn.COLUMN_TYPES):
            return JsonResponse({'success': False, 'error': 'Invalid column type'})
        
        # Create new column
        order = list_obj.columns.count()
        new_column = ListColumn.objects.create(
            user_list=list_obj,
            name=name,
            column_type=column_type,
            order=order
        )
        
        return JsonResponse({
            'success': True,
            'id': new_column.pk,
            'field': new_column.field,
            'name': new_column.name,
            'type': new_column.column_type
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error adding column: {e}")
        return JsonResponse({'success': False, 'error': 'Server error'})