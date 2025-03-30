"""
LR(1) items and operations module for the LR(1) parsing table generator.

This module contains classes and functions for working with LR(1) items,
computing closures, and constructing the LR(1) automaton.
"""

class LR1Item:
    """Represents an LR(1) item: (A → α•β, a) where a is the lookahead."""
    
    def __init__(self, production, dot_position, lookahead):
        """
        Initialize an LR(1) item.
        
        Args:
            production (tuple): A (lhs, rhs) tuple representing a production
            dot_position (int): Position of the dot in the RHS
            lookahead (str): The lookahead symbol
        """
        self.lhs = production[0]
        self.rhs = production[1]
        self.dot_position = dot_position
        self.lookahead = lookahead
    
    def __eq__(self, other):
        """Check equality with another LR(1) item."""
        if not isinstance(other, LR1Item):
            return False
        return (self.lhs == other.lhs and
                self.rhs == other.rhs and
                self.dot_position == other.dot_position and
                self.lookahead == other.lookahead)
    
    def __hash__(self):
        """Hash the LR(1) item for use in sets and dictionaries."""
        return hash((self.lhs, self.rhs, self.dot_position, self.lookahead))
    
    def get_next_symbol(self):
        """Get the symbol after the dot, or None if dot is at the end."""
        if self.dot_position < len(self.rhs):
            return self.rhs[self.dot_position]
        return None
    
    def advance_dot(self):
        """Create a new LR(1) item with the dot advanced one position."""
        return LR1Item((self.lhs, self.rhs), self.dot_position + 1, self.lookahead)
    
    def __str__(self):
        """Return a string representation of the LR(1) item."""
        rhs_with_dot = list(self.rhs)
        rhs_with_dot.insert(self.dot_position, "•")
        return f"({self.lhs} → {' '.join(rhs_with_dot)}, {self.lookahead})"
    
    def __repr__(self):
        """Return a string representation of the LR(1) item."""
        return self.__str__()

class LR1State:
    """Represents a state in the LR(1) automaton, containing a set of LR(1) items."""
    
    def __init__(self, items):
        """
        Initialize an LR(1) state.
        
        Args:
            items (set): A set of LR1Item objects
        """
        self.items = frozenset(items)  # Make it immutable for use as dict key
        self.transitions = {}  # Symbol -> target state
    
    def __eq__(self, other):
        """Check equality with another LR(1) state."""
        if not isinstance(other, LR1State):
            return False
        return self.items == other.items
    
    def __hash__(self):
        """Hash the LR(1) state for use in sets and dictionaries."""
        return hash(self.items)
    
    def __str__(self):
        """Return a string representation of the LR(1) state."""
        return "{" + ", ".join(str(item) for item in self.items) + "}"
    
    def __repr__(self):
        """Return a string representation of the LR(1) state."""
        return f"LR1State({len(self.items)} items)"

class LR1Automaton:
    """Represents the LR(1) automaton (state machine) for a grammar."""
    
    def __init__(self):
        """Initialize an empty LR(1) automaton."""
        self.states = []
        self.state_map = {}  # Mapping from state items to state index
    
    def add_state(self, state):
        """
        Add a state to the automaton if it doesn't already exist.
        
        Args:
            state (LR1State): The state to add
            
        Returns:
            int: The index of the state
        """
        # Check if this state already exists
        state_hash = hash(state.items)
        if state_hash in self.state_map:
            return self.state_map[state_hash]
        
        # Add the new state
        state_index = len(self.states)
        self.states.append(state)
        self.state_map[state_hash] = state_index
        return state_index

def compute_first_of_string(first_sets, grammar, string, lookahead):
# it compute lookahed of next state for example S -> A • B c, $  here we compute for c in example
# it compute lookahed of next state for example S -> A • B c, $  here we compute for c in example
    """
    Compute the FIRST set of a string of grammar symbols.
    
    Args:
        first_sets (dict): Dictionary of FIRST sets
        grammar (Grammar): Grammar object
        string (tuple): Tuple of grammar symbols
        lookahead (str): Lookahead symbol to include if string derives epsilon
        
    Returns:
        set: FIRST set of the string
    """
    if not string:
        return {lookahead}
    
    result = set()
    all_derive_epsilon = True
    
    for symbol in string:
        # Add all non-epsilon symbols from FIRST(symbol)
        result.update(first_sets[symbol] - {grammar.epsilon})
        
        # Check if this symbol can derive epsilon
        if grammar.epsilon not in first_sets[symbol]:
            all_derive_epsilon = False
            break
    
    # If all symbols can derive epsilon, add the lookahead
    if all_derive_epsilon:
        result.add(lookahead)
    
    return result

def compute_closure(items, grammar, first_sets):
    """
    Compute the closure of a set of LR(1) items.
    
    Args:
        items (set): Set of LR1Item objects
        grammar (Grammar): Grammar object
        first_sets (dict): Dictionary of FIRST sets
        
    Returns:
        set: Closure of the set of LR(1) items
    """
    closure = set(items)
    worklist = list(items)
    
    while worklist:
        item = worklist.pop()
        next_symbol = item.get_next_symbol() # get the next symbol example S -> A • B c, here next symbol is B
        
        # If the next symbol is a non-terminal
        if next_symbol in grammar.non_terminals:
            # Get the beta part after the dot and the lookahead
            beta = item.rhs[item.dot_position + 1:] if item.dot_position + 1 < len(item.rhs) else () # S -> A • B c, $ here beta is c
            # Get the lookahead symbol
            lookahead = item.lookahead
            
            # Find all productions B -> gamma for the non-terminal
            for lhs, rhs in grammar.get_productions_for(next_symbol):
                # Compute FIRST(beta lookahead)
                first_of_beta_a = compute_first_of_string(first_sets, grammar, beta, lookahead)
                
                # For each lookahead b in FIRST(beta lookahead)
                for b in first_of_beta_a:
                    new_item = LR1Item((lhs, rhs), 0, b)
                    if new_item not in closure:
                        closure.add(new_item)
                        worklist.append(new_item)
    
    return closure

def compute_goto(state_items, symbol, grammar, first_sets):
    """
    Compute the goto set for a state and a grammar symbol.
    
    Args:
        state_items (set): Set of LR1Item objects
        symbol (str): Grammar symbol (terminal or non-terminal)
        grammar (Grammar): Grammar object
        first_sets (dict): Dictionary of FIRST sets
        
    Returns:
        set: New set of LR1Item objects after the goto operation
    """
    goto_items = set()
    
    # Find items where the dot is before the given symbol
    for item in state_items:
        if item.get_next_symbol() == symbol:
            goto_items.add(item.advance_dot())
    
    # Compute closure of the new items
    return compute_closure(goto_items, grammar, first_sets)

def compute_lr1_automaton(grammar, first_sets):
    """
    Compute the LR(1) automaton for a grammar.
    
    Args:
        grammar (Grammar): Grammar object
        first_sets (dict): Dictionary of FIRST sets
        
    Returns:
        LR1Automaton: The constructed LR(1) automaton
    """
    automaton = LR1Automaton()
    
    # Create the initial item: S' -> •S, $
    initial_item = LR1Item((grammar.start_symbol, grammar.productions[0][1]), 0, '$')
    initial_items = compute_closure({initial_item}, grammar, first_sets)
    
    # Create the initial state
    initial_state = LR1State(initial_items) # create frozen set of this
    initial_state_idx = automaton.add_state(initial_state) # add state to states  if not exits already existing state simply return index
    # we store like We store mapping: X → 0 where X is the hash of the item

    # Process states until no new states are added
    worklist = [initial_state_idx]
    while worklist:
        state_idx = worklist.pop()
        state = automaton.states[state_idx]
        
        # Collect all symbols that appear after the dot
        symbols = set()
        for item in state.items:
            next_symbol = item.get_next_symbol()
            if next_symbol:
                symbols.add(next_symbol)
        
        # For each symbol, compute goto
        for symbol in symbols:
            next_items = compute_goto(state.items, symbol, grammar, first_sets)
            if not next_items:
                continue
                
            next_state = LR1State(next_items)
            next_state_idx = automaton.add_state(next_state)
            
            # Add transition from current state to next state
            state.transitions[symbol] = next_state_idx
            
            # Add new state to worklist if it was just created
            if next_state_idx == len(automaton.states) - 1:
                worklist.append(next_state_idx)
    
    # # Print automaton states and transitions
    # print("\n===== LR(1) AUTOMATON =====")
    # for i, state in enumerate(automaton.states):
    #     print(f"\nSTATE {i}:")
    #     for item in state.items:
    #         print(f"  {item}")
        
    #     print("\n  Transitions:")
    #     if state.transitions:
    #         for symbol, target in sorted(state.transitions.items()):
    #             print(f"    {symbol} → STATE {target}")
    #     else:
    #         print("    None")
    # print("\n=========================")
    
    return automaton
