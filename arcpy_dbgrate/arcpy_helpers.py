import arcpy

def add_field(table, field):
    print('Adding field {} to {}'.format(field['name'], table))
    domain = field['domain'] if 'domain' in field else None
    esri_type = field['type'] if 'type' in field else 'TEXT'
    esri_length = field['length'] if 'length' in field else 255

    arcpy.management.AddField(table, field['name'], esri_type, None, None, esri_length, field['alias'], field_domain=domain)

def add_fields(table, fields):
    print('Adding {} fields to {}'.format(len(fields), table))
    for field in fields:
        add_field(field, table)


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

    print('Adding unique index to {}'.format(name))
    arcpy.management.AddIndex(name, ['globalid'], "unique_globalid_{}".format(name), "UNIQUE", "ASCENDING")

    print('Adding fields to {}'.format(name))
    add_fields(fields, name)

def update_field(table, field):

    temp_field = field.copy()
    temp_field['name'] = 'temp_{}'.format(field['name'])

    # add the new temp field
    print('Add temp field {}'.format(temp_field['name']))
    add_field(temp_field, table)
    print('Calculate temp field to {}'.format(field['name']))
    arcpy.management.CalculateField(table, temp_field['name'], '!{}!'.format(field['name']), "PYTHON")

    # delete the old one
    print('Remove old field {}'.format(field['name']))
    arcpy.management.DeleteField(table, field['name'])

    # add the final field 
    new_field = field.copy()
    if 'rename' in field:
        new_field['name'] = field['rename']
    print('Add final field {}'.format(new_field['name']))
    add_field(new_field, table)
    print('Calculate new field from {}'.format(temp_field['name']))
    arcpy.management.CalculateField(table, new_field['name'], '!{}!'.format(temp_field['name']), 'PYTHON')

    # delete temp field
    print('Delete temp field {}'.format(temp_field['name']))
    arcpy.management.DeleteField(table, temp_field['name'])