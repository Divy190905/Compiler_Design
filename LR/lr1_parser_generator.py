#!/usr/bin/env python3

"""
LR(1) Parsing Table Generator

This script generates LR(1) parsing tables for context-free grammars.
It takes a grammar as input and produces the corresponding ACTION and GOTO tables.
"""

import sys
from grammar import Grammar
from first_follow import compute_first_sets, compute_follow_sets
from lr1_items import compute_lr1_automaton
from parsing_table import construct_parsing_table
from visualizer import display_parsing_table

# Import the visualization function from matplot.py
try:
    from matplot import enhance_parsing_table_display
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

def main():
    """Main function to orchestrate the LR(1) parsing table generation process."""
    print("=== LR(1) Parsing Table Generator ===")
    
    # Get grammar from user
    try:
        grammar_str = get_grammar_input()
        grammar = Grammar(grammar_str)
        print("\nParsed Grammar:")
        print(grammar)
    except Exception as e:
        print(f"Error parsing grammar: {e}")
        return
    
    # Compute FIRST and FOLLOW sets
    print("\nComputing FIRST sets...")
    first_sets = compute_first_sets(grammar)
    print("FIRST sets:", first_sets)
    
    print("\nComputing FOLLOW sets...")
    follow_sets = compute_follow_sets(grammar, first_sets)
    print("FOLLOW sets:", follow_sets)
    
    # Compute LR(1) automaton
    print("\nConstructing LR(1) automaton...")
    automaton = compute_lr1_automaton(grammar, first_sets)
    print(f"Created {len(automaton.states)} states in the LR(1) automaton")
    
    # Construct parsing table
    print("\nGenerating LR(1) parsing table...")
    action_table, goto_table, conflicts = construct_parsing_table(automaton, grammar)
    
    # Report conflicts if any
    if conflicts:
        print("\nConflicts detected:")
        for conflict in conflicts:
            print(f"  - {conflict}")
    else:
        print("\nNo conflicts detected.")
    
    # Display the parsing table
    print("\nLR(1) Parsing Table:")
    display_parsing_table(action_table, goto_table, grammar)
    
    print("\nLR(1) parsing table generation completed.")
    
    # Ask if user wants to see graphical visualization
    if HAS_MATPLOTLIB:
        print("\nGraphical visualization is available.")
        show_visual = input("Would you like to see a graphical visualization of the parsing table? (y/n): ").strip().lower()
        if show_visual in ['y', 'yes']:
            print("\nGenerating graphical visualization...")
            save_option = input("Do you want to save the visualization to a file? (y/n): ").strip().lower()
            output_file = None
            if save_option in ['y', 'yes']:
                output_file = input("Enter filename (e.g., 'parsing_table.png'): ").strip()
                if not output_file:
                    output_file = "lr1_parsing_table.png"
                print(f"Visualization will be saved to {output_file}")
            
            enhance_parsing_table_display(action_table, goto_table, grammar, output_file)
    else:
        print("\nGraphical visualization is not available. Install matplotlib to enable this feature.")
    # Add input testing functionality
    print("\n=== Input String Testing ===")
    print("Enter strings to test (or empty to quit):")
    while True:
        test_input = input("> ").strip()
        if not test_input:
            break
        grammar.test_input(test_input, action_table, goto_table, verbose=True)

def get_grammar_input():
    
    """Get grammar input from user in BNF-like format."""
    print("\nEnter your grammar rules, one per line.")
    print("Use the format: A -> B C | D")
    print("Enter an empty line to finish input.")
    print("Example:")
    print("  E -> E + T | T")
    print("  T -> T * F | F")
    print("  F -> ( E ) | id")
    
    lines = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        lines.append(line)
    
    if not lines:
        # Provide a default grammar for testing
        return """
        E -> E + T | T
        T -> T * F | F
        F -> ( E ) | id
        """
    
    return "\n".join(lines)

if __name__ == "__main__":
    main()
