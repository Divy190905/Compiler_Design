"""
Main module for the custom query language.
Uses a simplified direct parser if the LR parser has issues.
"""

from query_interpreter import QueryInterpreter
from query_sample_data import load_sample_data
from simplified_query_parser import parse_simple_query

def main():
    """Main function for the query language interpreter."""
    print("=== Custom SQL-like Query Language ===")
    
    # Create the interpreter
    interpreter = QueryInterpreter()
    
    # Load sample data
    load_sample_data(interpreter)
    
    # Interactive query loop
    print("\n=== Query Interpreter ===")
    print("Enter SQL-like queries (must end with ';')")
    print("Examples:")
    print("  SELECT * FROM employees;")
    print("  SELECT name, department FROM employees;")
    print("  SELECT salary FROM employees WHERE salary > 50000;")
    print("Type 'exit;' to quit")
    
    # Buffer for multi-line queries
    query_buffer = ""
    
    while True:
        line = input("> ").strip()
        
        # Append to buffer
        query_buffer += " " + line
        
        # Check if query is complete (ends with semicolon)
        if query_buffer.strip().endswith(";"):
            query = query_buffer.strip()
            query_buffer = ""
            
            # Check if user wants to exit
            if query.lower() == "exit;":
                print("Exiting query interpreter. Goodbye!")
                break
            
            # Parse and execute the query using our simplified parser
            success, parse_tree = parse_simple_query(query, interpreter.database)
            
            if success:
                try:
                    result = interpreter.execute_query(parse_tree)
                    print("\nQuery Result:")
                    if isinstance(result, list):
                        if not result:
                            print("No results found.")
                        else:
                            # Print column headers
                            headers = result[0].keys()
                            header_str = " | ".join(headers)
                            separator = "-" * len(header_str)
                            print(header_str)
                            print(separator)
                            
                            # Print each row
                            for row in result:
                                row_str = " | ".join(str(row.get(h, "")) for h in headers)
                                print(row_str)
                            print(f"\n{len(result)} rows returned.")
                    else:
                        print(result)
                except Exception as e:
                    print(f"Error executing query: {e}")
                    import traceback
                    traceback.print_exc()
    
    print("\nQuery language session completed.")

if __name__ == "__main__":
    main()
