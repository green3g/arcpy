from os.path import join
import arcpy
from os import getcwd

from environs import Env 
env = Env()
env.read_env()

username = env.str('DB_USERNAME', default='postgres')
password = env.str('DB_PASSWORD', default='secret')
db = env.str('DB_NAME', default='db')
host = env.str('DB_HOST', default='gisdata.db.com')
schema = env.str('DB_SCHEMA', default='dbo')

arcpy_user = env.str('ARCPY_USERNAME', default='dbo')
arcpy_password = env.str('ARCPY_PASSWORD', default='secret')

web_user = env.str('WEB_USER', default='db_user')

DB_CONNECTION_URL = 'postgresql://{username}:{password}@{host}:5432/{db}'.format(
    db=db,
    password=password,
    username=username,
    host=host,
)

temp = getcwd()
arcpy_connection = '{}__{}__{}.sde'.format(host, db, arcpy_user)

db_path = join(temp, arcpy_connection)

db_exists = arcpy.Exists(db_path)

print('Current database connection exists: {}'.format(db_exists))
if not db_exists:
    print('Creating db connection... {}/{}'.format(temp, arcpy_connection))
    arcpy.CreateDatabaseConnection_management(
        temp,
        arcpy_connection,
        'POSTGRESQL',
        host,
        'DATABASE_AUTH',
        arcpy_user,
        arcpy_password,
        'SAVE_USERNAME',
        db,
        schema,
    )
arcpy.env.workspace = db_path