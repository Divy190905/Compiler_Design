"""
Lexer for the query language.
"""

import re

def tokenize_query(query_string):
    """
    Tokenize the input query string.
    
    Returns a list of tokens as (token_type, token_value) pairs.
    """
    # Define token patterns
    token_specs = [
        ('WHITESPACE', r'\s+'),                   # Whitespace
        ('SELECT', r'SELECT'),                    # SELECT keyword
        ('FROM', r'FROM'),                        # FROM keyword
        ('WHERE', r'WHERE'),                      # WHERE keyword
        ('AND', r'AND'),                          # AND keyword
        ('OR', r'OR'),                            # OR keyword
        ('SEMICOLON', r';'),                      # Statement end
        ('COMMA', r','),                          # Comma
        ('PAREN_OPEN', r'\('),                    # Opening parenthesis
        ('PAREN_CLOSE', r'\)'),                   # Closing parenthesis
        ('OPERATOR', r'<=|>=|!=|=|<|>'),          # Comparison operators
        ('STAR', r'\*'),                          # Asterisk (SELECT *)
        ('NUMBER', r'\d+(\.\d*)?'),               # Integer or decimal numbers
        ('STRING', r'\'[^\']*\'|"[^"]*"'),        # String literals
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),# Identifiers
    ]
    
    # Create regex pattern
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)
    token_matcher = re.compile(token_regex, re.IGNORECASE)
    
    tokens = []
    pos = 0
    
    # Find all matches
    for match in token_matcher.finditer(query_string):
        token_type = match.lastgroup
        token_value = match.group(token_type)
        
        # Skip whitespace
        if token_type != 'WHITESPACE':
            # Convert keywords to uppercase
            if token_type in ('SELECT', 'FROM', 'WHERE', 'AND', 'OR'):
                token_value = token_value.upper()
            tokens.append((token_type, token_value))
        
        pos = match.end()
    
    # Check if the entire input was processed
    if pos < len(query_string):
        raise ValueError(f"Unexpected character '{query_string[pos]}' at position {pos}")
    
    return tokens
