"""
LR(1) items module for LR parser generator.

This module contains the LR1Item class and functions for generating LR(1) states,
including closure, goto, and LALR(1) state merging.
"""

class LR1Item:
    def __init__(self, lhs, rhs, dot_position, lookahead):
        self.lhs = lhs
        self.rhs = rhs
        self.dot_position = dot_position
        self.lookahead = lookahead
    
    def get_next_symbol(self):
        if self.dot_position < len(self.rhs):
            return self.rhs[self.dot_position]
        return None

def closure(grammar, items):
    """Compute the closure of a set of LR(1) items."""
    closure_set = set(items)
    worklist = list(items)  # Use a worklist for efficiency
    
    while worklist:
        item = worklist.pop()
        lhs, rhs, dot, lookahead = item
        
        # Check if there's a non-terminal after the dot
        if dot < len(rhs):
            symbol = rhs[dot]
            
            # If it's a non-terminal, add its productions to the closure
            if symbol in grammar.non_terminals:
                # Calculate FIRST of the part after the symbol
                beta = rhs[dot+1:] if dot+1 < len(rhs) else []
                
                # For each production of the non-terminal
                for prod in grammar.rules[symbol]:
                    # Calculate appropriate lookaheads
                    if beta:
                        # Calculate FIRST(beta lookahead)
                        first_of_beta = set()
                        all_have_epsilon = True
                        
                        for beta_symbol in beta:
                            if beta_symbol in grammar.terminals:
                                first_of_beta.add(beta_symbol)
                                all_have_epsilon = False
                                break
                            else:  # Non-terminal
                                first_beta_sym = grammar.first_sets[beta_symbol].copy()
                                if '' not in first_beta_sym:
                                    all_have_epsilon = False
                                    first_of_beta.update(first_beta_sym)
                                    break
                                else:
                                    first_beta_sym.remove('')
                                    first_of_beta.update(first_beta_sym)
                        
                        # Add original lookahead if all symbols in beta can derive epsilon
                        if all_have_epsilon:
                            first_of_beta.add(lookahead)
                            
                        new_lookaheads = first_of_beta
                    else:
                        # If beta is empty, use the current lookahead
                        new_lookaheads = {lookahead}
                    
                    # Add new items with calculated lookaheads
                    for new_la in new_lookaheads:
                        new_item = (symbol, tuple(prod), 0, new_la)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            worklist.append(new_item)
    
    return closure_set

def goto(grammar, items, symbol):
    """Compute the goto set for a state and a grammar symbol."""
    next_items = {(lhs, tuple(rhs), dot+1, lookahead) for lhs, rhs, dot, lookahead in items 
                 if dot < len(rhs) and rhs[dot] == symbol}
    return closure(grammar, next_items) if next_items else set()

def get_item_core(item):
    """Get the core of an item (ignoring lookahead)."""
    lhs, rhs, dot, _ = item
    return (lhs, rhs, dot)

def get_state_core(state):
    """Get the core of a state (set of item cores)."""
    return frozenset(get_item_core(item) for item in state)

def generate_lr1_items(grammar):
    """Generate LR(1) items for the grammar."""
    # Start with the initial item - using the correct attribute name
    # Note: Use grammar.rules which is the attribute defined in your Grammar class
    start_item = (grammar.start_symbol, tuple(grammar.rules[grammar.start_symbol][0]), 0, '$')
    start_closure = closure(grammar, {start_item})
    
    # Initialize the collection of states
    states = [start_closure]
    state_map = {frozenset(start_closure): 0}
    added = True
    
    # Generate all LR(1) states
    while added:
        added = False
        for state in states.copy():
            symbols = {sym for lhs, rhs, dot, _ in state if dot < len(rhs) for sym in (rhs[dot],)}
            for sym in symbols:
                goto_state = goto(grammar, state, sym)
                if goto_state and frozenset(goto_state) not in state_map:
                    state_map[frozenset(goto_state)] = len(states)
                    states.append(goto_state)
                    added = True
    
    return {i: state for i, state in enumerate(states)}

def generate_lalr1_items(grammar):
    """Generate LALR(1) items by merging LR(1) states with identical cores."""
    # First generate regular LR(1) items
    lr1_states = generate_lr1_items(grammar)
    
    # Now merge states with the same core
    result = {}
    core_to_state = {}  # Map from state core to state index
    
    # Process each original LR(1) state
    for i, state in lr1_states.items():
        state_core = get_state_core(state)
        
        if state_core in core_to_state:
            # Merge with existing state
            existing_state_idx = core_to_state[state_core]
            
            # Create a map from core to existing lookaheads
            core_to_lookaheads = {}
            for item in result[existing_state_idx]:
                lhs, rhs, dot, la = item
                core = (lhs, rhs, dot)
                if core not in core_to_lookaheads:
                    core_to_lookaheads[core] = set()
                core_to_lookaheads[core].add(la)
            
            # Add new lookaheads
            merged_state = set()
            for item in state:
                lhs, rhs, dot, la = item
                core = (lhs, rhs, dot)
                if core in core_to_lookaheads:
                    core_to_lookaheads[core].add(la)
                else:
                    core_to_lookaheads[core] = {la}
            
            # Build the merged state
            for core, lookaheads in core_to_lookaheads.items():
                lhs, rhs, dot = core
                for la in lookaheads:
                    merged_state.add((lhs, rhs, dot, la))
            
            result[existing_state_idx] = merged_state
        else:
            # New unique core
            core_to_state[state_core] = len(result)
            result[len(result)] = state
    
    # Store core_to_state mapping on the grammar for later use
    grammar.core_to_state = core_to_state
    
    # Calculate transitions for the merged states
    transitions = {}
    for i, state in result.items():
        transitions[i] = {}
        symbols = {sym for lhs, rhs, dot, _ in state if dot < len(rhs) for sym in (rhs[dot],)}
        
        for sym in symbols:
            goto_result = goto(grammar, state, sym)
            goto_core = get_state_core(goto_result)
            
            if goto_core in core_to_state:
                transitions[i][sym] = core_to_state[goto_core]
    
    # Store transitions for later use
    grammar.transitions = transitions
    
    return result
