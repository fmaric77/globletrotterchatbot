import boto3
import os
import time
import logging
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()
# Initialize the Athena client
athena_client = boto3.client(
    'athena',
    region_name=os.getenv('AWS_DEFAULT_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def query_athena(query: str) -> str:
    """Execute a query in Athena and return the results as a formatted string."""
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
        
        # Extract the data rows and store them in the global variable
        global stored_data
        stored_data = []
        for row in rows[1:]:
            row_data = {columns[i]: row['Data'][i]['VarCharValue'] for i in range(len(columns))}
            stored_data.append(row_data)
        
        return "Query executed and data stored successfully."
    except Exception as e:
        logging.error(f"Error executing Athena query: {str(e)}")
        return f"An error occurred while executing the query: {str(e)}"

@tool
def query_athena_tool(query: str) -> str:
    """Execute a query in Athena and return the results as a formatted string."""
    return query_athena(query)