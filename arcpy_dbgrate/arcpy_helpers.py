import arcpy

'''
    gets a field dict with defaults
'''
def get_field(input):
    return {
        'name': input.get('name'),
        'type': input.get('type', 'TEXT'),
        'alias': input.get('alias', input.get('name')),
        'domain': input.get('domain', None),
        'length': input.get('type', None),
    }
    


def add_field(table, field):
    print('Adding field {} to {}'.format(field['name'], table))
    field = get_field(field)
    arcpy.management.AddField(table, field['name'], field['type'], None, None, field['length'], field['alias'], field_domain=field['domain'])

def add_fields(table, fields):
    print('Adding {} fields to {}'.format(len(fields), table))
    for field in fields:
        add_field(table, field)


def add_domain(workspace, name, options):
    print('create {} in {}...'.format(name, workspace))
    arcpy.management.CreateDomain(workspace, name, name, 'TEXT', 'CODED')
    for domain in options:
        print('Adding domain value {}'.format(domain['name']))
        arcpy.management.AddCodedValueToDomain(workspace, name, domain['name'], domain['alias'])

def add_table(workspace, name, fields, feature_class=False, geometry_type='POINT', spatial_reference=4326):
    print('Creating table {}'.format(name))
    if feature_class:
        arcpy.management.CreateFeatureclass(workspace, name, geometry_type=geometry_type, spatial_reference=arcpy.SpatialReference(spatial_reference))
    else:
        arcpy.management.CreateTable(workspace, name)

    print('Adding global ids to {}'.format(name))
    arcpy.management.AddGlobalIDs(name)

    # print('Adding unique index to {}'.format(name))
    # arcpy.management.AddIndex(name, ['globalid'], "unique_globalid_{}".format(name), "UNIQUE", "ASCENDING")

    print('Adding fields to {}'.format(name))
    add_fields(name, fields)

def update_field(table, field):

    field = get_field(field)

    print('Updating field {}'.format(field['name']))
    # AlterField(in_table, field, {new_field_name}, {new_field_alias}, {field_type}, {field_length}, {field_is_nullable}, {clear_field_alias})
    arcpy.management.AlterField(table, field['name'], field['name'], field['alias'], field['length'])