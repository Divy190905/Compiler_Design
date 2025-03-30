"""
Visualization module for the LR(1) parsing table generator.

This module contains functions to display the generated parsing tables
in a readable format.
"""

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Pandas not available. Tables will be displayed in text format.")

def format_action(action):
    """Format an action for display."""
    if action is None:
        return ""
    
    action_type, value = action
    if action_type == 'shift':
        return f"s{value}"
    elif action_type == 'reduce':
        return f"r{value}"
    elif action_type == 'accept':
        return "acc"
    else:
        return str(action)

def display_parsing_table(action_table, goto_table, grammar):
    """
    Display the parsing table in a readable format.
    
    Args:
        action_table (dict): The ACTION table mapping (state, terminal) to action
        goto_table (dict): The GOTO table mapping (state, non-terminal) to state
        grammar (Grammar): The grammar object
    """
    # Get the list of states
    states = sorted(set(state for state, _ in action_table.keys()))
    
    # Get the list of terminals and non-terminals
    terminals = sorted(grammar.terminals) + ['$']
    non_terminals = sorted([nt for nt in grammar.non_terminals if nt != grammar.start_symbol])
    
    # Create a fixed-width table layout
    print("\nLR(1) PARSING TABLE:")
    print("=" * 80)
    
    # Print header
    header = f"{'State':^6}"
    for terminal in terminals:
        header += f" | {terminal:^5}"
    for non_terminal in non_terminals:
        header += f" | {non_terminal:^5}"
        
    print(header)
    print("-" * len(header))
    
    # Print rows
    for state in states:
        row = f"{state:^6}"
        
        # ACTION columns
        for terminal in terminals:
            if (state, terminal) in action_table:
                action = format_action(action_table[(state, terminal)])
                row += f" | {action:^5}"
            else:
                row += f" | {' ':^5}"
        
        # GOTO columns
        for non_terminal in non_terminals:
            if (state, non_terminal) in goto_table:
                goto = str(goto_table[(state, non_terminal)])
                row += f" | {goto:^5}"
            else:
                row += f" | {' ':^5}"
        
        print(row)
    
    print("=" * 80)
    
    # Print section labels
    section_labels = f"{'':^6}"
    for _ in terminals:
        section_labels += f" | {'':^5}"
    section_labels += f" | {'':^5}"
    print(section_labels)
    
    # Print production table
    print("\nPRODUCTIONS:")
    print("-" * 40)
    for i, (lhs, rhs) in enumerate(grammar.productions):
        rhs_str = " ".join(rhs) if rhs else "ε"
        print(f"{i:2d}. {lhs} → {rhs_str}")
    print("-" * 40)
