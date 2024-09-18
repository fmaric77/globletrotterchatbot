import psycopg2
import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RDSQueryManager:
    def __init__(self):
        self.connection = psycopg2.connect(
            host='database-1-instance-1.cj26esgeg1lm.us-east-1.rds.amazonaws.com',
            user='globetrotters_app',
            password='JaSamAplikacija',
            dbname=os.getenv('RDS_DATABASE'),  # Replace with your RDS database name
            port=5432  # PostgreSQL default port
        )
        self.max_execution_time = int(os.getenv('MAX_EXECUTION_TIME', 300))  # 5 minutes default
        self.max_results = int(os.getenv('MAX_RESULTS', 1000))
        
        # Set the search path to the specified schema
        self.set_search_path('globetrotters')

    def set_search_path(self, schema: str):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {schema};")
                self.connection.commit()
        except Exception as e:
            logging.error(f"Error setting search path: {str(e)}")
            raise

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logging.error(f"Error executing RDS query: {str(e)}")
            raise

    def close_connection(self):
        self.connection.close()