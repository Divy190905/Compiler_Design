"""
Grammar definition for a simple SQL-like query language.
"""

def get_query_grammar():
    """Return the grammar definition for our query language."""
    # Add an augmented start symbol for the parser
    grammar = """<S> -> <query>

<query> -> <select_statement> ;

<select_statement> -> SELECT <select_list> FROM <table_name> <where_clause>
<select_statement> -> SELECT <select_list> FROM <table_name>

<select_list> -> <column_name>
<select_list> -> <column_name> , <select_list>
<select_list> -> *

<table_name> -> IDENTIFIER

<column_name> -> IDENTIFIER

<where_clause> -> WHERE <condition>

<condition> -> <expr>
<condition> -> <expr> AND <condition>
<condition> -> <expr> OR <condition>
<condition> -> ( <condition> )

<expr> -> <column_name> = <value>
<expr> -> <column_name> > <value>
<expr> -> <column_name> < <value>
<expr> -> <column_name> >= <value>
<expr> -> <column_name> <= <value>
<expr> -> <column_name> != <value>

<value> -> IDENTIFIER
<value> -> NUMBER
<value> -> STRING"""
    return grammar
