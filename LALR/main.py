"""
Main module for LR parser generator.

This module orchestrates the entire process of grammar parsing,
LR(1) state generation, parsing table construction, and input parsing.
"""

from grammar import Grammar
from items import generate_lalr1_items
from parsing_tables import construct_parsing_tables
from parser import parse_input
from display import (
    display_lr1_states, display_parsing_tables, 
    display_parsing_steps, get_grammar_input
)

def main():
    """Main function for the LR(1) parser generator."""
    print("=== LALR(1) Parser Generator and String Parser ===")
    
    # Get grammar from user
    grammar_str = get_grammar_input()
    
    # Create grammar object
    print("\nParsing grammar...")
    grammar = Grammar(grammar_str)
    
    # Compute LALR(1) items
    print("\nCalculating LALR(1) items...")
    lalr1_states = generate_lalr1_items(grammar)
    
    # Display the states
    print(f"\nGenerated {len(lalr1_states)} LALR(1) states")
    display_lr1_states(lalr1_states)
    
    # Construct parsing tables
    print("\nConstructing parsing tables...")
    action_table, goto_table, conflicts = construct_parsing_tables(grammar, lalr1_states)
    
    # Report conflicts if any
    if conflicts:
        print("\nConflicts detected:")
        for conflict in conflicts:
            print(f"  - {conflict}")
    else:
        print("\nNo conflicts detected.")
    
    # Display the parsing tables
    display_parsing_tables(action_table, goto_table, grammar.terminals, grammar.non_terminals)
    
    # Interactive parsing loop
    print("\n=== Interactive Parser Mode ===")
    print("Enter strings to parse (space-separated tokens)")
    print("Type 'q', 'quit', or 'exit' to end the session")
    
    while True:
        print("\nEnter a string to parse (or 'q' to quit):")
        input_string = input("> ").strip()
        
        # Check if the user wants to quit
        if input_string.lower() in ['q', 'quit', 'exit']:
            print("Exiting parser. Goodbye!")
            break
        
        # Skip empty inputs
        if not input_string:
            print("Empty input. Please enter tokens separated by spaces.")
            continue
        
        # Parse the input string
        success, steps = parse_input(grammar, action_table, goto_table, input_string)
        
        # Display the result
        if success:
            print("\nParsing successful! The string is valid according to the grammar.")
        else:
            print("\nParsing failed! The string is not valid according to the grammar.")
        
        # Ask if user wants to see detailed steps
        print("\nDo you want to see the parsing steps? (y/n)")
        show_steps = input("> ").strip().lower()
        if show_steps.startswith('y'):
            display_parsing_steps(steps)
    
    print("\nLALR(1) parsing session completed.")

if __name__ == "__main__":
    main()