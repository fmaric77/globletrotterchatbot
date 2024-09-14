from langchain.tools import tool
from x_help import AthenaQueryManager
import json

def format_results(results):
    if not results:
        return "No results returned."
    
    # Get the column names from the first row
    columns = list(results[0].keys())
    
    # Calculate the maximum width for each column
    column_widths = {col: max(len(col), max(len(str(row[col])) for row in results)) for col in columns}
    
    # Create the header
    header = " | ".join(col.ljust(column_widths[col]) for col in columns)
    separator = "-+-".join("-" * column_widths[col] for col in columns)
    
    # Create the rows
    rows = [
        " | ".join(str(row[col]).ljust(column_widths[col]) for col in columns)
        for row in results
    ]
    
    # Combine everything
    table = f"{header}\n{separator}\n" + "\n".join(rows)
    
    return table

@tool
def query_athena_tool(query: str) -> str:
    """Execute a query in Athena and return the results as a formatted string."""
    try:
        athena_manager = AthenaQueryManager()
        results = athena_manager.execute_query(query)
        
        formatted_results = format_results(results)
        
        return f"Query executed successfully. Results:\n\n{formatted_results}"
    except Exception as e:
        return f"An error occurred while executing the query: {str(e)}"

# Example usage
if __name__ == "__main__":
    query = "SELECT * FROM coaches LIMIT 5"
    print(query_athena_tool(query))