
import boto3
import os
import time
import logging
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AthenaQueryManager:
    def __init__(self):
        self.athena_client = boto3.client(
            'athena',
            region_name=os.getenv('AWS_DEFAULT_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.database = os.getenv('ATHENA_DATABASE')
        self.output_location = os.getenv('ATHENA_OUTPUT_LOCATION')
        self.max_execution_time = int(os.getenv('MAX_EXECUTION_TIME', 300))  # 5 minutes default
        self.max_results = int(os.getenv('MAX_RESULTS', 1000))

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        try:
            query_execution_id = self._start_query_execution(query)
            self._wait_for_query_completion(query_execution_id)
            return self._get_query_results(query_execution_id)
        except Exception as e:
            logging.error(f"Error executing Athena query: {str(e)}")
            raise

    def _start_query_execution(self, query: str) -> str:
        try:
            response = self.athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': self.database},
                ResultConfiguration={'OutputLocation': self.output_location}
            )
            return response['QueryExecutionId']
        except ClientError as e:
            logging.error(f"Error starting query execution: {e}")
            raise

    def _wait_for_query_completion(self, query_execution_id: str) -> None:
        start_time = time.time()
        while True:
            query_status = self.athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = query_status['QueryExecution']['Status']['State']
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            if time.time() - start_time > self.max_execution_time:
                self.athena_client.stop_query_execution(QueryExecutionId=query_execution_id)
                raise TimeoutError(f"Query execution timed out after {self.max_execution_time} seconds")
            time.sleep(2)

        if status != 'SUCCEEDED':
            error_message = query_status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
            raise Exception(f"Query failed with status: {status}. Reason: {error_message}")

    def _get_query_results(self, query_execution_id: str) -> List[Dict[str, Any]]:
        paginator = self.athena_client.get_paginator('get_query_results')
        rows = []
        columns = []

        for page in paginator.paginate(QueryExecutionId=query_execution_id, PaginationConfig={'MaxItems': self.max_results}):
            result_set = page['ResultSet']
            
            if not columns:
                columns = [col['Label'] for col in result_set['ResultSetMetadata']['ColumnInfo']]
            
            for row in result_set['Rows'][1 if not rows else 0:]:  # Skip header row for first page
                row_data = {}
                for i, cell in enumerate(row['Data']):
                    row_data[columns[i]] = cell.get('VarCharValue', '')
                rows.append(row_data)

        return rows