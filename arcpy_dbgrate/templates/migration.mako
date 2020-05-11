"""
${comment}

Author: ${author}
Create Date: ${create_date}

Notice: Migration auto-generated using dbgrate
Add fields: ${len(add_fields)}
Remove fields: ${len(remove_fields)}
Update fields: ${len(update_fields)}

"""
import arcpy
% if len(update_fields):
from arcpy_dbgrate.arcpy_helpers import update_field
% endif
% if len(add_tables):
from arcpy_dbgrate.arcpy_helpers import add_table
% endif


def upgrade():
    % for item in add_tables:
    # add_table(workspace, name, fields, feature_class=False, geometry_type='POINT', spatial_reference=4326)
    <%
    is_feature = True if '_geometry' in item and item['_geometry'] is not None else False
    geometry_type = item['_geometry'] if '_geometry' in item else 'POINT' 
    spatial_reference = item['_srid'] if '_srid' in item else None
    %>
    print('Add table ${item['_name']}')
    add_table(arcpy.env.workspace, '${item['_name']}', ${item['fields']}, feature_class=${is_feature}, geometry_type='${geometry_type}', spatial_reference=${spatial_reference})

    % endfor

    % for item in add_fields:
    <% 
    field = item['field'] 
    table = item['table']
    domain = field['domain'] if 'domain' in field else None
    %>
    print('Adding field ${field['name']} to ${table}')
    arcpy.management.AddField('${table}', '${field['name']}', '${field['type']}', None, None, ${field['length']}, '${field['alias']}', field_domain='${domain}')
    % endfor

    % for item in remove_fields:
    <% 
    field = item['field'] 
    table = item['table']
    %>
    print('Deleting field ${field['name']} from ${table}')
    arcpy.management.DeleteField('${table}', ['${field['name']}'])
    % endfor

    % for item in update_fields:
    <% 
    field = item['field'] 
    table = item['table']
    %>
    print('Updating field ${field['name']} from ${table}')
    update_field('${table}', ${field})
    % endfor

def downgrade():
    % for item in add_tables:
    print('Delete table ${item['_name']}')
    arcpy.management.Delete('${item['_name']}')
    % endfor

    % for item in remove_fields:
    <% 
    field = item['field'] 
    table = item['table']
    domain = field['domain'] if 'domain' in field else None
    %>
    print('Adding field ${field['name']} to ${table}')
    arcpy.management.AddField('${table}', '${field['name']}', '${field['type']}', None, None, ${field['length']}, '${field['alias']}', field_domain='${domain}')
    % endfor

    % for item in add_fields:
    <% 
    field = item['field'] 
    table = item['table']
    %>
    print('Deleting field ${field['name']} from ${table}')
    arcpy.management.DeleteField('${table}', ['${field['name']}'])
    % endfor