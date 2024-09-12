import boto3
from langchain.tools import tool
import os
import csv
import pandas as pd
import uuid
import time

# Initialize the Athena client
athena_client = boto3.client(
    'athena',
    region_name=os.getenv('AWS_DEFAULT_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

@tool
def query_athena(query: str) -> list:
    """Execute a query in Athena and return the results as a list of dictionaries."""
    try:
        # Set the Athena parameters
        database = os.getenv('ATHENA_DATABASE')
        output_location = os.getenv('ATHENA_OUTPUT_LOCATION')
        
        # Start the query execution
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_location}
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # Wait for the query to complete
        while True:
            query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = query_status['QueryExecution']['Status']['State']
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            time.sleep(2)
        
        if status != 'SUCCEEDED':
            raise Exception(f"Query failed with status: {status}")
        
        # Get the query results
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        rows = results['ResultSet']['Rows']
        
        # Extract the column names
        column_info = rows[0]['Data']
        columns = [col['VarCharValue'] for col in column_info]
        
        # Extract the data rows
        data = []
        for row in rows[1:]:
            data.append({columns[i]: row['Data'][i]['VarCharValue'] for i in range(len(columns))})
        
        return data
    except Exception as e:
        print(f"Error executing Athena query: {str(e)}")
        return []