import boto3
from langchain.tools import tool
import os
import csv
import pandas as pd
import uuid

# Initialize the Glue client
glue_client = boto3.client(
    'glue',
    region_name=os.getenv('AWS_DEFAULT_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

@tool
def get_glue_catalog_database(database_name: str) -> dict:
    """Get details of a specified Glue Data Catalog database and save its tables' content as CSV files."""
    try:
        # Get the list of tables in the database
        tables_response = glue_client.get_tables(DatabaseName=database_name)
        tables = tables_response['TableList']
        
        for table in tables:
            table_name = table['Name']
            # Get the table schema
            table_response = glue_client.get_table(DatabaseName=database_name, Name=table_name)
            table_schema = table_response['Table']['StorageDescriptor']['Columns']
            
            # Hardcoded S3 location
            s3_location = f"s3://olympics-travel-mockdb/{table_name}.csv"
            print(f"Processing table: {table_name}, S3 location: {s3_location}")
            
            # Read the data from S3
            data = read_s3_data(s3_location)
            
            if not data:
                print(f"No data found for table: {table_name}")
                continue
            
            # Generate a random name for the CSV file
            csv_file = f"{database_name}_{table_name}_{uuid.uuid4().hex}.csv"
            with open(csv_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=[col['Name'] for col in table_schema])
                writer.writeheader()
                writer.writerows(data)
                print(f"Data for table {table_name} saved to {csv_file}")
        
        return {"status": "success", "message": f"Data from database {database_name} saved to CSV files."}
    except glue_client.exceptions.EntityNotFoundException:
        return {"error": f"Database {database_name} not found."}
    except Exception as e:
        return {"error": f"Error accessing Glue Data Catalog: {str(e)}"}

def read_s3_data(s3_location: str) -> list:
    """Read data from an S3 location and return it as a list of dictionaries."""
    try:
        # Read the CSV file from S3 using pandas
        print(f"Reading data from S3 location: {s3_location}")
        df = pd.read_csv(s3_location)
        print(f"Data read from S3: {df.head()}")
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error reading data from S3: {str(e)}")
        return []