"""
Query interpreter for the custom query language.
"""

class QueryInterpreter:
    """Interprets and executes queries against an in-memory database."""
    
    def __init__(self):
        """Initialize with an empty in-memory database."""
        self.database = {}
    
    def load_table(self, table_name, data):
        """Load data into a table."""
        self.database[table_name] = data
        print(f"Table '{table_name}' loaded with {len(data)} rows.")
    
    def execute_query(self, parse_tree):
        """Execute a query from its parse tree."""
        # The root node should be 'query'
        if parse_tree[0] != 'query':
            raise ValueError("Invalid parse tree, expected 'query' as root node")
        
        # Extract the select statement
        select_stmt = parse_tree[1]
        
        if select_stmt[0] != 'select_statement':
            raise ValueError("Invalid parse tree, expected 'select_statement'")
        
        # Extract components of the SELECT statement
        select_list = None
        table_name = None
        where_clause = None
        
        # Parse the components based on the structure of the parse tree
        for item in select_stmt[1:]:
            if isinstance(item, tuple) and item[0] == 'select_list':
                select_list = self._parse_select_list(item)
            elif isinstance(item, tuple) and item[0] == 'table_name':
                table_name = item[1]
            elif isinstance(item, tuple) and item[0] == 'where_clause':
                where_clause = item[1]
        
        # Execute the query
        return self._execute_select(select_list, table_name, where_clause)
    
    def _parse_select_list(self, select_list_node):
        """Parse the select list from the parse tree."""
        columns = []
        
        # Handle SELECT * case
        if len(select_list_node) == 2 and select_list_node[1] == '*':
            return '*'
        
        # Handle SELECT column1, column2, ... case
        node = select_list_node
        while True:
            if node[1][0] == 'column_name':
                columns.append(node[1][1])
            
            # If there are more columns
            if len(node) > 2 and node[2][0] == 'select_list':
                node = node[2]
            else:
                break
        
        return columns
    
    def _evaluate_condition(self, condition, row):
        """Evaluate a condition against a row."""
        if condition[0] == 'condition':
            # Handle nested conditions
            if condition[1][0] == 'expr':
                return self._evaluate_expression(condition[1], row)
            elif condition[1] == '(':
                return self._evaluate_condition(condition[2], row)
            
            # Handle AND/OR operations
            left_result = self._evaluate_expression(condition[1], row)
            operator = condition[2]
            right_result = self._evaluate_condition(condition[3], row)
            
            if operator == 'AND':
                return left_result and right_result
            elif operator == 'OR':
                return left_result or right_result
        
        elif condition[0] == 'expr':
            return self._evaluate_expression(condition, row)
        
        return False
    
    def _evaluate_expression(self, expr, row):
        """Evaluate a basic expression against a row."""
        if expr[0] != 'expr':
            return False
        
        column_name = expr[1][1]
        operator = expr[2]
        value_node = expr[3]
        
        # Check if column exists in the row
        if column_name not in row:
            return False
        
        # Get the literal value
        if value_node[0] == 'value':
            if value_node[1][0] == 'NUMBER':
                try:
                    value = int(value_node[1][1])
                except ValueError:
                    value = float(value_node[1][1])
            elif value_node[1][0] == 'STRING':
                # Remove quotes
                value = value_node[1][1][1:-1]
            else:
                value = value_node[1][1]
        else:
            value = value_node[1]
        
        # Validate data types
        if isinstance(row[column_name], (int, float)) and not isinstance(value, (int, float)):
            raise ValueError(f"Type mismatch: Column '{column_name}' is numeric, but value '{value}' is not")
        if isinstance(row[column_name], str) and not isinstance(value, str):
            raise ValueError(f"Type mismatch: Column '{column_name}' is string, but value '{value}' is not")
        
        # Apply the comparison
        if operator == '=':
            return row[column_name] == value
        elif operator == '>':
            return row[column_name] > value
        elif operator == '<':
            return row[column_name] < value
        elif operator == '>=':
            return row[column_name] >= value
        elif operator == '<=':
            return row[column_name] <= value
        elif operator == '!=':
            return row[column_name] != value
        
        return False
    
    def _execute_select(self, select_list, table_name, where_clause):
        """Execute a SELECT query."""
        # Check if the table exists
        if table_name not in self.database:
            return f"Error: Table '{table_name}' not found"
        
        table = self.database[table_name]
        result = []
        
        # Apply the WHERE clause if it exists
        filtered_rows = table
        if where_clause:
            filtered_rows = [row for row in table if self._evaluate_condition(where_clause, row)]
        
        # Apply the SELECT clause
        if select_list == '*':
            return filtered_rows
        else:
            for row in filtered_rows:
                result_row = {}
                for col in select_list:
                    if col not in row:
                        return f"Error: Column '{col}' does not exist in table '{table_name}'"
                    result_row[col] = row[col]
                result.append(result_row)
        
        return result
