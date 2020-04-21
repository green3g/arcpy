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
from arcpy_dbgrate.arcpy_helpers import update_field

def upgrade():
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