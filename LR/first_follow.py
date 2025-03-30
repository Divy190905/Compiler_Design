"""
First and Follow set computation for the LR(1) parsing table generator.

This module contains functions to compute the FIRST and FOLLOW sets
for a given context-free grammar.
"""

def compute_first_sets(grammar):
    """
    Compute the FIRST sets for all symbols in the grammar.
    
    Args:
        grammar (Grammar): The grammar object
        
    Returns:
        dict: A dictionary mapping symbols to their FIRST sets
    """
    # Initialize FIRST sets
    first = {symbol: set() for symbol in grammar.non_terminals}
    
    # Add terminals to their own FIRST sets
    for terminal in grammar.terminals:
        first[terminal] = {terminal}
    
    # Add epsilon to its FIRST set
    first[grammar.epsilon] = {grammar.epsilon}
    
    # Repeat until no more changes occur
    while True:
        changes = False
        
        for lhs, rhs in grammar.productions:
            # Case 1: If rhs starts with epsilon, add epsilon to FIRST(lhs)
            if rhs[0] == grammar.epsilon:
                if grammar.epsilon not in first[lhs]:
                    first[lhs].add(grammar.epsilon)
                    changes = True
                continue
            
            # Case 2: Process the right-hand side symbols
            # Initialize to track if all symbols can derive epsilon
            all_derive_epsilon = True
            
            for symbol in rhs:
                if symbol not in first:
                    # This handles symbols not seen before (likely terminals)
                    first[symbol] = {symbol}
                
                # Add all non-epsilon symbols from FIRST(symbol) to FIRST(lhs)
                for terminal in first[symbol] - {grammar.epsilon}:
                    if terminal not in first[lhs]:
                        first[lhs].add(terminal)
                        changes = True
                
                # If this symbol cannot derive epsilon, stop processing
                if grammar.epsilon not in first[symbol]:
                    all_derive_epsilon = False
                    break
            
            # If all symbols can derive epsilon, add epsilon to FIRST(lhs)
            if all_derive_epsilon and len(rhs) > 0:
                if grammar.epsilon not in first[lhs]:
                    first[lhs].add(grammar.epsilon)
                    changes = True
        
        # If no changes were made in this iteration, we're done
        if not changes:
            break
    
    return first

def compute_follow_sets(grammar, first_sets):
    """
    Compute the FOLLOW sets for all non-terminals in the grammar.
    
    Args:
        grammar (Grammar): The grammar object
        first_sets (dict): Dictionary of FIRST sets
        
    Returns:
        dict: A dictionary mapping non-terminals to their FOLLOW sets
    """
    # Initialize FOLLOW sets for all non-terminals
    follow = {nt: set() for nt in grammar.non_terminals}
    
    # Add $ (end of input) to FOLLOW set of the start symbol
    follow[grammar.start_symbol].add('$')
    
    # Repeat until no more changes occur
    while True:
        changes = False
        
        for lhs, rhs in grammar.productions:
            # For each symbol in the right-hand side
            for i, symbol in enumerate(rhs):
                # Skip terminals, they don't have FOLLOW sets
                if symbol not in grammar.non_terminals:
                    continue
                
                # Initialize a flag to check if all symbols after this one can derive epsilon
                all_following_derive_epsilon = True
                
                # Process all symbols that follow the current one
                if i < len(rhs) - 1:
                    # Add FIRST of all following symbols (if they can derive epsilon)
                    for j in range(i + 1, len(rhs)):
                        next_symbol = rhs[j]
                        
                        # Add FIRST(next_symbol) - {ε} to FOLLOW(symbol)
                        old_size = len(follow[symbol])
                        follow[symbol].update(first_sets[next_symbol] - {grammar.epsilon})
                        if len(follow[symbol]) > old_size:
                            changes = True
                        
                        # If this symbol cannot derive epsilon, stop the chain
                        if grammar.epsilon not in first_sets[next_symbol]:
                            all_following_derive_epsilon = False
                            break
                else:
                    # If this is the last symbol, all following symbols trivially derive epsilon
                    all_following_derive_epsilon = True
                
                # If all following symbols can derive epsilon (or this is the last symbol)
                # then add FOLLOW(lhs) to FOLLOW(symbol)
                if all_following_derive_epsilon:
                    old_size = len(follow[symbol])
                    follow[symbol].update(follow[lhs])
                    if len(follow[symbol]) > old_size:
                        changes = True
        
        # If no changes were made in this iteration, we're done
        if not changes:
            break
    
    return follow
