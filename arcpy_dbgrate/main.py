import click
import logging
from importlib import import_module
from os.path import join
from sys import path
from os import getcwd, environ
from arcpy_dbgrate.compare_models import generate_migration
from arcpy_dbgrate.create_models import create_models
from dbgrate.main import cli 

# modify the local path so we can import our env.py
WORKING_DIR = getcwd()
path.append(WORKING_DIR)

@cli.command()
create_models

if __name__ == '__main__':
    logging.info('arcpy: Current working directory is {}'.format(WORKING_DIR))

    # create cli with context
    cli()
