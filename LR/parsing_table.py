"""
Parsing table generation module for the LR(1) parsing table generator.

This module contains functions to generate the ACTION and GOTO tables
from the LR(1) automaton.
"""

def construct_parsing_table(automaton, grammar):
    """
    Construct the LR(1) parsing table from the automaton.
    
    Args:
        automaton (LR1Automaton): The LR(1) automaton
        grammar (Grammar): The grammar object
        
    Returns:
        tuple: (action_table, goto_table, conflicts)
            - action_table: Dictionary mapping (state, symbol) to action
            - goto_table: Dictionary mapping (state, non_terminal) to state
            - conflicts: List of conflict descriptions
    """
    action_table = {}  # (state, terminal) -> action
    goto_table = {}    # (state, non_terminal) -> state
    conflicts = []
    
    # For each state in the automaton
    for state_idx, state in enumerate(automaton.states):
        # For each item in the state
        for item in state.items:
            next_symbol = item.get_next_symbol()
            
            # Case 1: [A → α•aβ, b] - Shift action
            if next_symbol in grammar.terminals:
                # Check if there's a transition on this terminal
                if next_symbol in state.transitions:
                    next_state = state.transitions[next_symbol]
                    action = ('shift', next_state)
                    
                    # Check for shift-reduce or reduce-reduce conflict
                    if (state_idx, next_symbol) in action_table:
                        existing_action = action_table[(state_idx, next_symbol)]
                        if existing_action[0] == 'reduce':
                            conflicts.append(f"Shift-reduce conflict in state {state_idx} on symbol {next_symbol}")
                            # Resolve conflict in favor of shift (for now)
                        elif existing_action[0] == 'reduce' and action[0] == 'reduce':
                            conflicts.append(f"Reduce-reduce conflict in state {state_idx} on symbol {next_symbol}")
                            # Keep existing reduction (for now)
                            continue
                    
                    action_table[(state_idx, next_symbol)] = action
            
            # Case 2: [A → α•, a] - Reduce action
            elif next_symbol is None:
                # Special case for augmented start production [S' → S•, $] - Accept
                if item.lhs == grammar.start_symbol and item.rhs == grammar.productions[0][1] and item.lookahead == '$':
                    action_table[(state_idx, '$')] = ('accept', None)
                else:
                    # Get the production number for the reduce action
                    production_num = grammar.get_production_number(item.lhs, item.rhs)
                    action = ('reduce', production_num)
                    
                    # Check for shift-reduce or reduce-reduce conflict
                    if (state_idx, item.lookahead) in action_table:
                        existing_action = action_table[(state_idx, item.lookahead)]
                        if existing_action[0] == 'shift':
                            conflicts.append(f"Shift-reduce conflict in state {state_idx} on symbol {item.lookahead}")
                            # Resolve conflict in favor of shift (for now)
                            continue
                        elif existing_action[0] == 'reduce':
                            conflicts.append(f"Reduce-reduce conflict in state {state_idx} on symbol {item.lookahead}")
                            # Keep existing reduction (for now)
                            # LR(1) can still have conflicts: While LR(1) is more powerful than SLR or LALR(1), it can still have shift-reduce and reduce-reduce conflicts for ambiguous grammars.
                            continue
                    
                    action_table[(state_idx, item.lookahead)] = action
        
        # For each transition on a non-terminal, add a goto entry
        for symbol, next_state in state.transitions.items():
            if symbol in grammar.non_terminals:
                goto_table[(state_idx, symbol)] = next_state
    
    return action_table, goto_table, conflicts
