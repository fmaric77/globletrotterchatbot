import boto3
from langchain.tools import tool
import os
import textwrap

# Initialize the Glue client
glue_client = boto3.client(
    'glue',
    region_name=os.getenv('AWS_DEFAULT_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

@tool
def get_glue_catalog_database(database_name: str) -> str:
    """Get details of a specified Glue Data Catalog database."""
    try:
        response = glue_client.get_database(Name=database_name)
        database = response['Database']
        formatted_output = textwrap.dedent(f"""
            Database Name: {database['Name']}
            Description : {database.get('Description', 'No description')}
            Location URI: {database.get('LocationUri', 'No location URI')}
        """).strip()
        return formatted_output
    except glue_client.exceptions.EntityNotFoundException:
        return f"Database {database_name} not found."
    except Exception as e:
        return f"Error accessing Glue Data Catalog: {str(e)}"