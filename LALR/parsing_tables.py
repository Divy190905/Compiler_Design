"""
Parsing tables module for LR parser generator.

This module contains functions for generating ACTION and GOTO tables
from LR(1) states.
"""

from items import goto, get_state_core

def construct_parsing_tables(grammar, states):
    """
    Construct ACTION and GOTO tables based on the computed LR(1) or LALR(1) states.
    
    Args:
        grammar: Grammar object
        states: The LR(1) or LALR(1) states
        
    Returns:
        Tuple of (action_table, goto_table, conflicts)
    """
    # Initialize ACTION and GOTO tables
    action_table = {}
    goto_table = {}
    conflicts = []
    
    # Get all terminals and non-terminals
    all_terminals = grammar.terminals.copy()
    all_terminals.add('$')  # EOF marker
    all_non_terminals = grammar.non_terminals.copy()
    
    # Initialize tables with empty dictionaries
    for state_idx in states:
        action_table[state_idx] = {}
        goto_table[state_idx] = {}
    
    # Function to register a conflict
    def register_conflict(state, symbol, action1, action2):
        conflicts.append(f"Conflict in state {state} on symbol '{symbol}': {action1} vs {action2}")
    
    # Fill the ACTION and GOTO tables
    for state_idx, state in states.items():
        # Process transitions (for shift actions and goto)
        symbols = {sym for lhs, rhs, dot, _ in state if dot < len(rhs) for sym in (rhs[dot],)}
        
        for symbol in symbols:
            # Compute the goto state for this symbol
            goto_state = goto(grammar, state, symbol)
            
            # Get the core of the goto state
            goto_core = get_state_core(goto_state)
            
            if goto_state and goto_core in grammar.core_to_state:
                next_state = grammar.core_to_state[goto_core]
                
                if symbol in all_terminals:
                    # Terminal symbol -> Shift action
                    action = f"shift {next_state}"
                    
                    if symbol in action_table[state_idx]:
                        register_conflict(state_idx, symbol, action_table[state_idx][symbol], action)
                    
                    action_table[state_idx][symbol] = action
                else:
                    # Non-terminal symbol -> Goto action
                    goto_table[state_idx][symbol] = next_state
        
        # Process reduce actions for items with dot at the end
        for lhs, rhs, dot, lookahead in state:
            if dot == len(rhs):  # Dot at the end, so we have a reduce action
                # Special case for augmented start rule (Accept action)
                if lhs == grammar.start_symbol and dot == len(rhs) and lookahead == '$':
                    # Check if this is for the initial production of the start symbol
                    if len(rhs) == 1 and rhs[0] in grammar.non_terminals:
                        action_table[state_idx]['$'] = "accept"
                        continue
                
                # Regular reduce action
                prod_num = grammar.get_production_number(lhs, list(rhs))
                action = f"reduce {prod_num}"
                
                if lookahead in action_table[state_idx]:
                    register_conflict(state_idx, lookahead, action_table[state_idx][lookahead], action)
                
                action_table[state_idx][lookahead] = action
    
    return action_table, goto_table, conflicts
