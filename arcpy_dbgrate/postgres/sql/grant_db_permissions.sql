--Add requisite Postgis extensions
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION postgis_sfcgal;

--Set default Geometry storage to PostGIS geometry
UPDATE sde.sde_dbtune SET
config_string = 'PG_GEOMETRY' WHERE
keyword = 'DEFAULTS' AND parameter_name = 'GEOMETRY_STORAGE';

--Create data admin schema and set auth on the schema
CREATE SCHEMA dbo
    AUTHORIZATION dbo;


--revoke public access
REVOKE CONNECT ON DATABASE database_name FROM PUBLIC;
GRANT connect ON DATABASE database_name TO dbo;
GRANT connect ON DATABASE database_name TO db_user;


GRANT USAGE ON SCHEMA sde TO db_user;
GRANT USAGE ON SCHEMA dbo TO db_user;
GRANT SELECT ON TABLE public.geography_columns TO db_user;
GRANT SELECT ON TABLE public.geometry_columns TO db_user;
GRANT SELECT ON TABLE public.spatial_ref_sys TO db_user;

--Grant full edit privileges on user account for all objects
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA dbo
TO db_user;

--Alter default privileges for user account for future objects owned by dbo
ALTER DEFAULT PRIVILEGES
    FOR USER dbo
    IN SCHEMA dbo
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES to db_user;


-- create necessary function(s)
-- FUNCTION: public.test_viewdef(regclass)
-- DROP FUNCTION public.test_viewdef(regclass);
CREATE OR REPLACE FUNCTION public.test_viewdef(
    view_to_test regclass)
    RETURNS boolean
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE
AS $BODY$
DECLARE
    dummy VARCHAR;
    sql_expr VARCHAR;
BEGIN
    SET transaction_read_only = on ;
    sql_expr := trim(trailing ';' from pg_get_viewdef(view_to_test));
   EXECUTE format('SELECT * FROM (%%s) foo LIMIT 1', sql_expr) INTO dummy;
   RETURN TRUE;
END
$BODY$;
ALTER FUNCTION public.test_viewdef(regclass)
    OWNER TO postgres;
	
SELECT 1 success;