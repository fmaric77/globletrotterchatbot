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
    """Execute a query in Athena and return only the query results.
    Select the appropriate table based on the user's query without describing the table or the query logic in the response.

    The 'athletes' table contains general data regarding athletes who competed in the 2024 Olympic Games. Use the 'name' column with the name of the athlete, the 'gender' column with the gender of the athlete, the 'country' column with the country of the athlete, the 'disciplines' column which contains a list of sports in which the athlete competed in.
    For example, if the user asked you to 'list all athletes from Iceland who competed in rowing in the 2024 Olympic Games' you would run the following query on the 'athletes' table:
    SELECT name FROM 'athletes' WHERE country = 'Iceland' AND disciplines LIKE '%Rowing%'

    The 'city_counts' table contains the number of medals people born in a specific city won in a specific discipline in the last 3 Olympic Games. Use the 'birth_place' column to determine the name of the city where the medal winners came from, the 'discipline' column to determine what sport the medals were won in, and the 'count' column to determine the total number of medals won by people from this city in the specified sport.
    For example, if the user asked you to 'find the city which gave the most Olympic medalists in athletics recently', you would run the following query on the 'city_counts' table:
    SELECT birth_place FROM 'city_counts' WHERE discipline = 'Athletics' ORDER BY DESC LIMIT 1

    The 'coaches' table contains general data regarding people who coached athletes who competed in the 2024 Olympic Games. Use the 'name' column with the name of the coach, the 'gender' column with the gender of the coach, the 'country' column with the country of the coach, the 'discipline' column which contains a list of sports in which the coach coached.
    For example, if the user asked you to 'list all the coaches from Croatia who were part of the 2024 Olympic Games' you would run the following query on the 'coaches' table:
    SELECT name FROM 'coaches' WHERE country = 'Croatia'

    The 'medal_counts' table contains the total number of medals each country won in a specific discipline in the last 3 Olympic Games. Use the 'country' column with the name of the country which won medals, the 'discipline' column to determine what sport the medals were won in, and the 'count' column to determine the total number of medals won by this country in the specified sport.
    For example, if the user asked you to 'find which country has the most Olympic medals in water polo recently', you would run the following query on the 'medal_counts' table:
    SELECT country FROM 'medal_counts' WHERE discipline = 'Water Polo' ORDER BY DESC LIMIT 1

    The 'medallists' table contains specific data regarding all medal winners in the 2024 Olympic Games only. Use the 'medal_type' column to determine the type of the medal won, the 'name' column to determine the name of the athlete or country which won the medal, the 'discipline' column to determine in which sport the medal was won, the 'country' column to determine the country of the winner.
    For example, if the user asked you to 'list all gold medal winners in diving in the 2024 Olympic Games', you would run the following query:
    SELECT name FROM 'medallists' WHERE medal_type = 'Gold Medal' AND discipline LIKE '%Diving%'

    Always return only the query results regardless of the size, not an explanation or the query itself.
    """
    try:
        athena_manager = AthenaQueryManager()
        results = athena_manager.execute_query(query)
        
        formatted_results = format_results(results)
        
        return f"Query executed successfully. Results:\n\n{formatted_results}"
    except Exception as e:
        return f"An error occurred while executing the query: {str(e)}"

# Example usage
#if __name__ == "__main__":
#    query = "SELECT * FROM coaches LIMIT 5"
#    print(query_athena_tool(query))