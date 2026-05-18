from functools import lru_cache
from langchain_core.tools import tool

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

from app.config import settings
from app.logger import logger


@lru_cache(maxsize=1)
def get_database() -> SQLDatabase:
    logger.info(
        "initializing athena connection", extra={"database": settings.glue_database}
    )
    conn_str = (
        f"awsathena+rest://@athena.{settings.aws_region}.amazonaws.com:443"
        f"?s3_staging_dir={settings.athena_output_bucket}"
        f"&work_group={settings.athena_workgroup}"
        f"&catalog_name=AwsDataCatalog"
        f"&schema_name={settings.glue_database}"
    )
    engine = create_engine(conn_str)
    return SQLDatabase(engine=engine)


@tool
def list_tables() -> str:
    """Liste toutes les tables disponibles dans le Glue catalog."""
    logger.info("listing tables", extra={"database": settings.glue_database})
    return ", ".join(get_database().get_usable_table_names())


@tool
def get_table_schema(table_name: str) -> str:
    """Retourne le schéma d'une table (colonnes et types)."""
    logger.info("fetching schema", extra={"table": table_name})
    return get_database().get_table_info(table_names=[table_name])


@tool
def run_sql_query(query: str) -> str:
    """Exécute une requête SQL sur Athena et retourne les résultats."""
    logger.info("running query", extra={"query": query})
    return get_database().run(query)
