import click
import logging
from importlib import import_module
from os.path import join
from sys import path
from os import getcwd, environ
from dbgrate.main import cli 

# modify the local path so we can import our env.py
WORKING_DIR = getcwd()
path.append(WORKING_DIR)

@cli.command()
def create_models():
    """
    generate a base set of models from existing database tables
    """
    from arcpy_dbgrate.create_models import create_models as _create_models
    _create_models()

@cli.command()
@click.option('--name', default=None, help='Migration name')
@click.option('--comment', default=None, help='Comment text for migration.')
def auto_migration(name=None, comment=None):
    """
    automatically create an arcpy migration from model changes
    """
    from arcpy_dbgrate.compare_models import create_migration
    name = name or click.prompt('Migration name')
    comment = comment or click.prompt('Comment')
    create_migration(name, comment)

if __name__ == '__main__':
    logging.info('arcpy: Current working directory is {}'.format(WORKING_DIR))

    # create cli with context
    cli()
