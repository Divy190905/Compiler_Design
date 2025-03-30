"""
Parser module for LR parser generator.

This module contains functions for parsing input strings using
ACTION and GOTO tables.
"""

def parse_input(grammar, action_table, goto_table, input_string):
    """
    Parse an input string according to the grammar and parsing tables.
    
    Args:
        grammar: Grammar object
        action_table: ACTION table mapping (state, terminal) to actions
        goto_table: GOTO table mapping (state, non-terminal) to states
        input_string: Input string to parse
        
    Returns:
        Tuple of (success, steps) where success is a boolean indicating if parsing was successful
        and steps is a list of parsing steps for debugging/display
    """
    # Tokenize the input
    tokens = input_string.split()
    tokens.append('$')  # Add end marker
    
    # Initialize the stack with state 0
    stack = [0]
    
    # Keep track of parsing steps for display
    steps = []
    
    # Current position in the input
    position = 0
    
    while True:
        current_state = stack[-1]
        current_symbol = tokens[position]
        
        steps.append({
            'stack': stack.copy(),
            'input': tokens[position:],
            'action': "?"
        })
        
        # Look up action in the ACTION table
        if current_state not in action_table or current_symbol not in action_table[current_state]:
            steps[-1]['action'] = "Error: No action defined"
            return False, steps
        
        action = action_table[current_state][current_symbol]
        steps[-1]['action'] = action
        
        if action == "accept":
            # Parsing successful
            return True, steps
        
        elif action.startswith("shift"):
            # Shift action: push the symbol and next state onto the stack
            next_state = int(action.split()[1])
            stack.append(current_symbol)
            stack.append(next_state)
            position += 1
            
        elif action.startswith("reduce"):
            # Reduce action: pop symbols, push non-terminal, and goto new state
            production_num = int(action.split()[1])
            
            # Find the production
            lhs = None
            rhs = None
            
            # Iterate through grammar rules to find the production with this number
            prod_count = 0
            for nt, productions in grammar.rules.items():
                for prod in productions:
                    if prod_count == production_num:
                        lhs = nt
                        rhs = prod
                        break
                    prod_count += 1
                if lhs:
                    break
            
            if not lhs:
                steps[-1]['action'] = f"Error: Invalid production number {production_num}"
                return False, steps
            
            # Pop 2 * |rhs| items from the stack (symbol and state for each RHS symbol)
            for _ in range(2 * len(rhs)):
                stack.pop()
            
            # Get the current state after popping
            prev_state = stack[-1]
            
            # Push the LHS non-terminal
            stack.append(lhs)
            
            # Look up in GOTO table and push the new state
            if prev_state not in goto_table or lhs not in goto_table[prev_state]:
                steps[-1]['action'] = f"Error: No GOTO defined for state {prev_state} and non-terminal {lhs}"
                return False, steps
            
            next_state = goto_table[prev_state][lhs]
            stack.append(next_state)
            
        else:
            # Invalid action
            steps[-1]['action'] = f"Error: Invalid action {action}"
            return False, steps
    
    # Should never reach here
    return False, steps
