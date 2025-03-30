"""
A simplified SQL query parser that directly processes queries without using the LR parser.
"""

from query_lexer import tokenize_query

def parse_simple_query(query_string, database):
    """
    Parse a simple SQL query using a direct approach.
    Perform semantic checks for table and column existence.
    """
    try:
        # Tokenize the query
        tokens = tokenize_query(query_string)
        print("\nTokenized query:")
        for token_type, token_value in tokens:
            print(f"  ({token_type}, {token_value})")
        
        # Basic validation
        if not tokens:
            print("Error: Empty query")
            return False, None
            
        # Check if it's a SELECT query
        if tokens[0][0] != 'SELECT':
            print("Error: Query must start with SELECT")
            return False, None
            
        # Find the FROM token
        from_index = -1
        for i, (token_type, _) in enumerate(tokens):
            if token_type == 'FROM':
                from_index = i
                break
                
        if from_index == -1:
            print("Error: Query must contain FROM clause")
            return False, None
            
        # Extract table name
        if from_index + 1 >= len(tokens) or tokens[from_index + 1][0] != 'IDENTIFIER':
            print("Error: Missing table name after FROM")
            return False, None
            
        table_name = tokens[from_index + 1][1]
        
        # Check if the table exists in the database
        if table_name not in database:
            print(f"Error: Table '{table_name}' does not exist in the database")
            return False, None
        
        # Extract column list (between SELECT and FROM)
        select_list_tokens = tokens[1:from_index]
        
        # Handle SELECT * case
        if len(select_list_tokens) == 1 and select_list_tokens[0][0] == 'STAR':
            select_list = ('select_list', '*')
        else:
            # Process column list with commas
            columns = []
            i = 0
            while i < len(select_list_tokens):
                if select_list_tokens[i][0] == 'IDENTIFIER':
                    column_name = select_list_tokens[i][1]
                    
                    # Check if the column exists in the table
                    if column_name not in database[table_name][0]:
                        print(f"Error: Column '{column_name}' does not exist in table '{table_name}'")
                        return False, None
                    
                    columns.append(column_name)
                i += 1
                # Skip comma if present
                if i < len(select_list_tokens) and select_list_tokens[i][0] == 'COMMA':
                    i += 1
            
            if not columns:
                print("Error: No valid columns specified")
                return False, None
            
            # Create a simplified select_list structure compatible with the interpreter
            if len(columns) == 1:
                select_list = ('select_list', ('column_name', columns[0]))
            else:
                # Build the nested structure for the interpreter
                last_col = ('column_name', columns[-1])
                select_list = ('select_list', last_col)
                
                # Add the rest of the columns in reverse order
                for col in reversed(columns[:-1]):
                    select_list = ('select_list', ('column_name', col), ',', select_list)
        
        # Find WHERE clause if any
        where_index = -1
        for i, (token_type, _) in enumerate(tokens):
            if token_type == 'WHERE':
                where_index = i
                break
                
        # Handle WHERE clause
        where_clause = None
        if where_index != -1:
            # Get tokens for the condition (excluding semicolon)
            end_index = len(tokens) - 1 if tokens[-1][0] == 'SEMICOLON' else len(tokens)
            condition_tokens = tokens[where_index + 1:end_index]
            
            if not condition_tokens:
                print("Error: Empty WHERE condition")
                return False, None
                
            condition = parse_simple_condition(condition_tokens)
            if condition:
                where_clause = ('where_clause', condition)
            else:
                print("Error: Invalid WHERE condition syntax")
                return False, None
        
        # Build the full parse tree
        if where_clause:
            select_stmt = ('select_statement', 'SELECT', select_list, 'FROM', ('table_name', table_name), where_clause)
        else:
            select_stmt = ('select_statement', 'SELECT', select_list, 'FROM', ('table_name', table_name))
            
        parse_tree = ('query', select_stmt)
        
        print(f"Parse tree: {parse_tree}")
        return True, parse_tree
        
    except Exception as e:
        print(f"Error parsing query: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def parse_simple_condition(tokens):
    """Parse a simple condition for the WHERE clause."""
    if not tokens:
        return None
        
    # Basic case: column operator value
    if len(tokens) >= 3:
        if tokens[0][0] == 'IDENTIFIER' and tokens[1][0] == 'OPERATOR':
            column = ('column_name', tokens[0][1])
            operator = tokens[1][1]
            
            # Get value token
            if tokens[2][0] == 'NUMBER':
                value = ('value', ('NUMBER', tokens[2][1]))
            elif tokens[2][0] == 'STRING':
                value = ('value', ('STRING', tokens[2][1]))
            elif tokens[2][0] == 'IDENTIFIER':
                value = ('value', ('IDENTIFIER', tokens[2][1]))
            else:
                print(f"Error: Unsupported value type: {tokens[2][0]}")
                return None
                
            expr = ('expr', column, operator, value)
            
            # If this is it, return a simple condition
            if len(tokens) == 3:
                return ('condition', expr)
                
            # Check for AND/OR
            if len(tokens) > 3:
                if tokens[3][0] == 'AND' and len(tokens) > 4:
                    rest = parse_simple_condition(tokens[4:])
                    if rest:
                        return ('condition', expr, 'AND', rest)
                elif tokens[3][0] == 'OR' and len(tokens) > 4:
                    rest = parse_simple_condition(tokens[4:])
                    if rest:
                        return ('condition', expr, 'OR', rest)
                    
            # Just return the expression if we can't parse more
            return ('condition', expr)
    
    print(f"Warning: Could not parse condition tokens: {tokens}")
    return None

def test_parser():
    """Test the parser with sample queries."""
    test_queries = [
        "SELECT * FROM employees;",
        "SELECT name, department FROM employees;",
        "SELECT name FROM employees WHERE department = 'Engineering';",
        "SELECT name, salary FROM employees WHERE salary > 70000;",
        "SELECT * FROM products WHERE price > 200 AND category = 'Electronics';"
    ]
    
    # Sample database schema for testing
    database = {
        'employees': (['name', 'department', 'salary'], []),
        'products': (['price', 'category'], [])
    }
    
    for query in test_queries:
        print(f"\n\nTesting query: {query}")
        success, tree = parse_simple_query(query, database)
        if success:
            print("QUERY PARSING SUCCESSFUL!")
        else:
            print("QUERY PARSING FAILED!")

if __name__ == "__main__":
    test_parser()
