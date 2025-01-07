import psycopg2
from kfp import dsl


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        'psycopg2-binary',  # Ensure psycopg2 is installed
        'loguru',
    ],
)
def test_db_connection() -> None:
    from loguru import logger
    import psycopg2


    """Test the connection to the Cloud SQL database"""
    # Database connection details
    db_host = "34.135.189.108"  # Replace with your Cloud SQL IP
    db_name = "mlflow-db"
    db_user = "mlops-end2end-sql"
    db_password = "57913Asd@"  # Use the correct password

    try:
        # Establish the database connection
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port="5432"  # Default PostgreSQL port
        )
        logger.info("Connection to database successful")
        connection.close()
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise