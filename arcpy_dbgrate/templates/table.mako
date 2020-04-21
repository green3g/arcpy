# AUTO GENERATED FILE

class ${table['name']}:
    # table properties
    _name = '${table['name']}'
    % if 'geometry' in table:
    _geometry = '${table['geometry']}'
    _srid = ${table['srid']}
    % endif

    # relationships
    % for rel in table['relationships']:
    _rel_${rel['name']} = ${rel}
    % endfor

    # fields in table
    % for field in table['fields']:
    ${field['name']} = ${field}
    % endfor
