import env
import arcpy
from .create_models import get_layers, map_fields, filter_fields
from glob import glob
from os import getcwd, environ
from os.path import join, basename , isfile
from importlib import import_module
from mako.template import Template
from datetime import datetime
import logging

from .constants import PACKAGE_DIR

field_skip_keys = [
    'name',
]

table_keys = [
    '_name',
    '_geometry',
    '_srid',
    '_relationships',
]

def filter_field_keys(key):
    return key not in field_skip_keys

def find_field(fields, field_name):
    for field in fields:
        if field['name'] == field_name:
            return field

def compare_key(a, b, key):
    a_val = a[key] if key in a else None
    b_val = b[key] if key in b else None 

    if a_val is None:
        # if no a val was provided - we don't need to update the b_val
        return True

    return a_val == b_val
    
def compare_models():
    add_tables = []
    remove_tables = []
    add_fields = []
    remove_fields = []
    update_fields = []

    add_tables = []
    remove_tables = []

    models = [basename(f)[:-3] for f in glob(join(getcwd(), 'models', "*.py")) if isfile(f) and not f.endswith('__init__.py')]

    # collect existing data
    existing_fc = [table.split('.')[-1].upper() for table in arcpy.ListFeatureClasses()]
    existing_tables = [table.split('.')[-1].upper() for table in arcpy.ListTables()]
    
    for model in models:
        logging.debug('Checking {}'.format(model))
        table = getattr( import_module('models.{}'.format(model)), model)
        table_name = getattr(table, '_name')
        field_names = [f for f in dir(table) if not f.startswith('_')]

        # collect table props
        table_props = {}
        for prop in [key for key in dir(table) if key in table_keys]:
            table_props[prop] = getattr(table, prop)
        table_props['fields'] = [getattr(table, f) for f in field_names]
        
        # see if we need to create the table
        found_table = False
        if '_geometry' not in table_props or not table_props['_geometry']:
            found_table = table_props['_name'].upper() in existing_tables
        else:
            found_table = table_props['_name'].upper() in existing_fc
        if not found_table:
            logging.info('Add: {}'.format(table_props['_name']))
            add_tables.append(table_props)
            continue

        existing_fields = list(filter(filter_fields, map(map_fields, arcpy.ListFields(table_name))))

        # check for new or updated fields
        for field_name in field_names:
            field_obj = getattr(table, field_name)
            field_obj['name'] = field_name
            existing = find_field(existing_fields, field_name)
            if not existing:
                logging.info('Add: {}.{}'.format(table_name, field_name))
                add_fields.append({'table': table_name, 'field': field_obj})
            else:
                should_update = False
                for key in filter(filter_field_keys, field_obj.keys()):
                    if not compare_key(field_obj, existing, key):
                        logging.debug('Difference: {}.{}, Old Value: {}, New Value: {}'.format(
                            table_name,
                            key, 
                            existing[key] if key in field_obj else 'Undefined',
                            field_obj[key] if key in field_obj else 'Undefined',
                        ))
                        should_update = True
                if should_update:
                    logging.info('Update: {}.{}'.format(table_name, field_name))
                    update_fields.append({'table': table_name, 'field': field_obj})
                else:
                    logging.debug('Match: {}.{}'.format(table_name, field_name))

        # check for fields that need to be deleted
        for field in existing_fields:
            field_name = field['name']
            try:
                defined_field = getattr(table, field_name)
            except:
                # field doesn't exist
                logging.info('Remove: {}.{}'.format(table_name, field_name))
                remove_fields.append({'table': table_name, 'field': field})

    logging.info("""
        Updates Summary: 
            Fields:
                Add: {}
                Update: {}
                Remove: {}
            Tables:
                Add: {}
                Remove: {}
    """.format(
        len(add_fields),
        len(update_fields),
        len(remove_fields),
        len(add_tables),
        len(remove_tables),
    ))
    return {
        'add_fields': add_fields,
        'update_fields': update_fields,
        'remove_fields': remove_fields,
        'add_tables': add_tables,
        'remove_tables': remove_tables,
    }


def generate_migration(name, data={}, template=None):
    """
    Generate a new migrations file. Migrations will be prefixed with a timestamp.
    """


    timestamp = str(datetime.now().timestamp()).replace('.', '_')
    file_name = '{}_{}.py'.format(timestamp, name.replace('.', '_').replace(' ', '_').lower())
    logging.info('generating migration migrations/{}'.format(file_name))

    # get the template content
    if template is None:
        template_path = join(dirname(realpath(__file__)), 'templates', 'migration.py.mako')
        with open(template_path, 'r') as f:
            template = Template(f.read(), strict_undefined=True)

    data['create_date'] = datetime.now().ctime()

    # write it to a migration file
    logging.debug('rendering template with data', data)
    with open(join('migrations', file_name), 'w') as f:
        f.write(template.render(**data))

    logging.info('Created new migration file migrations/{}'.format(file_name))
    return file_name

def create_migration(name='Update Migration from arcpy', comment='This migration was autogenerated by scanning arcpy models and comparing schemas. It should not be modified'):
    migrations = compare_models()
    template_path = join(PACKAGE_DIR, 'templates', 'migration.mako')
    template = Template(filename=template_path, strict_undefined=True)
    migrations['comment'] = comment
    migrations['author'] =  environ.get('USER') or environ.get('USERNAME')
    generate_migration(name, migrations, template)


if __name__ == '__main__':
    create_migration()