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

# Check for matplotlib availability
HAS_MATPLOTLIB = False
try:
    import matplotlib.pyplot as plt
    from matplot import visualize_parsing_tables, visualize_parsing_process
    HAS_MATPLOTLIB = True
except ImportError:
    pass

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
                
                # Create and save the visualization
                visualize_parsing_tables(action_table, goto_table, grammar.terminals, grammar.non_terminals, output_file)
                print(f"Visualization saved to {output_file}")
            else:
                # Just display the visualization
                visualize_parsing_tables(action_table, goto_table, grammar.terminals, grammar.non_terminals)
    else:
        print("\nGraphical visualization is not available. Install matplotlib to enable this feature.")
    
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
            
            # Offer visualization of parsing steps if matplotlib is available
            if HAS_MATPLOTLIB:
                show_process_visual = input("Would you like to see a graphical visualization of the parsing process? (y/n): ").strip().lower()
                if show_process_visual in ['y', 'yes']:
                    save_option = input("Do you want to save the parsing process visualization to a file? (y/n): ").strip().lower()
                    if save_option in ['y', 'yes']:
                        process_file = input("Enter filename (e.g., 'parsing_process.png'): ").strip()
                        if not process_file:
                            process_file = "parsing_process.png"
                        visualize_parsing_process(steps, process_file)
                        print(f"Parsing process visualization saved to {process_file}")
                    else:
                        visualize_parsing_process(steps)
    
    print("\nLALR(1) parsing session completed.")

if __name__ == "__main__":
    main()