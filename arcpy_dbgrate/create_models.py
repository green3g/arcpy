import arcpy
from mako.template import Template
from importlib import import_module

try:
    import_module('env')
except:
    print('Error! Cannot import env module. Ensure env.py exists in current working directory')
    
field_types = {
    'String': 'TEXT',
}

exclude_field_types = [
    'GLOBALID',
    'OID',
    'GEOMETRY',
]
exclude_field_partials = [
    '(',
]

def get_field_type(field):
    return field_types[field.type] if field.type in field_types else field.type.upper()

def filter_fields(field):
    for exclusion_string in exclude_field_partials:
        if exclusion_string in field['name'].upper():
            return False
    return field['type'] not in exclude_field_types

def map_fields(field):
    return {
        'name': field.name,
        'alias': field.aliasName,
        'type': get_field_type(field),
        'domain': field.domain if field.domain else None,
        'length': field.length,
    }


exclude_item_partials = [
    '__ATTACH',
    '_VW',
]
def filter_layers(layer_name):
    for exclusion_string in exclude_item_partials:
        if exclusion_string in layer_name.upper():
            return False
    return True


rel_cardinality = {
    'OneToOne': 'ONE_TO_ONE',
    'OneToMany': 'ONE_TO_MANY',
    'ManyToMany': 'MANY_TO_MANY',
}

def filter_primary_key(rule):
    return rule[1] == 'OriginPrimary'

def filter_foreign_key(rule):
    return rule[1] == 'OriginForeign'

def map_relationships(rel):
    rel_name = rel.name.split('.')[-1]
    return {
        'name': rel_name,
        'cardinality': rel_cardinality[rel.cardinality],
        'forward_label': rel.forwardPathLabel,
        'backward_label': rel.backwardPathLabel,
        # WTF
        'primary_key': list(filter(filter_primary_key, rel.originClassKeys))[0][0],
        'foreign_key': list(filter(filter_foreign_key, rel.originClassKeys))[0][0],
    }

def get_layers():
    layers = [item for item in filter(filter_layers, arcpy.ListTables())] + [item for item in filter(filter_layers, arcpy.ListFeatureClasses())]
    return layers

def create_models():
    template = Template(filename='./generator/table.mako')
    layers = get_layers()

    for item in layers:
        name = item.split('.')[-1]
        desc = arcpy.Describe(name)
        table = {
            'name': name,
            'type': desc.dataType,
            'geometry': desc.shapeType if desc.dataType == 'FeatureClass' else None,
            'srid': desc.spatialReference.factoryCode if desc.dataType == 'FeatureClass' else None,
        }

        # add relationships
        try:
            relationships = list(map(map_relationships, [arcpy.Describe(name) for name in desc.relationshipClassNames]))
        except Exception as e:
            print('Error getting relationships', e)
            relationships = []
            continue
        table['relationships'] = relationships
        
        try:
            # arcgis errors out on this sometimes...wtf 
            fields = arcpy.ListFields(table['name'])
        except Exception as e:
            print('Error on ListFields', e)
            fields =  []
            continue

        # build field info
        table['fields'] = list(filter(filter_fields, map(map_fields,  fields)))

        print('Writing model for {}'.format(name))
        with open('./models/{}.py'.format(name), 'w') as f:
            f.write(template.render(table = table))


if __name__ == '__main__':
    create_models()