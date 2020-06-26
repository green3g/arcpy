from os.path import join
from os.path import dirname, realpath

PACKAGE_DIR = dirname(realpath(__file__))

def upgrade(env, engine):
    with open(join(PACKAGE_DIR, 'sql', 'grant_db_permissions.sql'), 'r') as f:
        sql = f.read()
        sql = sql.replace('database_name', env.db).replace('db_user', env.web_user)

        print('Executing sql...')
        
        with engine.begin() as connection:
            connection.execute(sql)


def downgrade(engine):
    print('Deleting schema dbo...')
    sql = """
        --Add requisite Postgis extensions
        DROP SCHEMA IF EXISTS dbo CASCADE; 
        DROP EXTENSION postgis_sfcgal;
        DROP EXTENSION postgis_topology;
        DROP EXTENSION postgis;
        SELECT 1 success;
    """
    with engine.begin() as connection:
        connection.execute(sql)