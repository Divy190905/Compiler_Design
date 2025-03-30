"""
Display module for LR parser generator.

This module contains functions for displaying grammar, items, states,
parsing tables, and parsing steps.
"""

def display_lr1_states(lr1_states):
    """Display the LR(1) states in a clean format."""
    print("\nLR(1) STATES:")
    print("============")
    
    for state_idx, state in lr1_states.items():
        print(f"State {state_idx}:")
        for item in sorted(state):
            lhs, rhs, dot, lookahead = item
            rhs_str = " ".join(list(rhs[:dot]) + ["•"] + list(rhs[dot:]))
            print(f"  {lhs} -> {rhs_str}, {lookahead}")
        print()  # Add extra line for readability

def display_parsing_tables(action_table, goto_table, terminals, non_terminals):
    """
    Display the parsing tables in a readable format.
    
    Args:
        action_table: The ACTION table mapping (state, terminal) to actions
        goto_table: The GOTO table mapping (state, non-terminal) to states
        terminals: Set of terminal symbols
        non_terminals: Set of non-terminal symbols
    """
    terminals = sorted(list(terminals) + ['$'])
    non_terminals = sorted(list(non_terminals))
    
    print("\nACTION TABLE:")
    print("=============")
    
    # Print header
    header = "State | " + " | ".join(f"{term:10}" for term in terminals)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for state in sorted(action_table.keys()):
        row = f"{state:5} | "
        for term in terminals:
            action = action_table[state].get(term, "")
            row += f"{action:10} | "
        print(row)
    
    print("\nGOTO TABLE:")
    print("===========")
    
    # Print header
    header = "State | " + " | ".join(f"{nt:5}" for nt in non_terminals)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for state in sorted(goto_table.keys()):
        row = f"{state:5} | "
        for nt in non_terminals:
            goto = goto_table[state].get(nt, "")
            row += f"{goto:5} | "
        print(row)

def display_parsing_steps(steps):
    """
    Display the steps of the parsing process.
    
    Args:
        steps: List of parsing steps
    """
    print("\nParsing Steps:")
    print("==============")
    
    for i, step in enumerate(steps):
        stack_str = ' '.join(str(item) for item in step['stack'])
        input_str = ' '.join(step['input'])
        action_str = step['action']
        
        print(f"Step {i}:")
        print(f"  Stack: {stack_str}")
        print(f"  Input: {input_str}")
        print(f"  Action: {action_str}")
        print()

def get_grammar_input():
    """Get grammar input from user in BNF-like format."""
    print("\nEnter your grammar rules, one per line.")
    print("Use the format: A -> B C | D")
    print("Enter an empty line to finish input.")
    print("Example:")
    print("  E' -> E")
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
        E' -> E
        E -> E + T | T
        T -> T * F | F
        F -> ( E ) | id
        """
    
    return "\n".join(lines)
