from collections import defaultdict

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

class Grammar:
    def __init__(self, grammar_str):
        self.rules = self.parse_grammar(grammar_str)
        self.start_symbol = list(self.rules.keys())[0]
        self.terminals, self.non_terminals = self.get_symbols()
        self.first_sets = self.compute_first_sets()

    def parse_grammar(self, grammar_str):
        rules = {}
        for line in grammar_str.strip().split("\n"):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            lhs, rhs = line.split("->")
            lhs = lhs.strip()
            productions = [prod.strip().split() for prod in rhs.strip().split("|")]
            rules[lhs] = productions
        return rules

    def get_symbols(self):
        terminals, non_terminals = set(), set(self.rules.keys())
        for rhs in self.rules.values():
            for prod in rhs:
                for symbol in prod:
                    if symbol not in non_terminals:
                        terminals.add(symbol)
        return terminals, non_terminals

    def compute_first_sets(self):
        first = defaultdict(set)

        def first_of(symbol, visited=None):
            if visited is None:
                visited = set()
            if symbol in self.terminals:
                return {symbol}
            if symbol in visited:
                return set()
            visited.add(symbol)
            
            if symbol in first:
                return first[symbol]

            for production in self.rules.get(symbol, []):
                for sym in production:
                    f = first_of(sym, visited.copy())
                    first[symbol] |= f - {''}
                    if '' not in f:
                        break
                else:
                    first[symbol].add('')
            
            return first[symbol]

        for non_terminal in self.non_terminals:
            first_of(non_terminal)

        return first

    def get_production_number(self, lhs, rhs):
        for index, (non_terminal, productions) in enumerate(self.rules.items()):
            if non_terminal == lhs:
                for prod_index, production in enumerate(productions):
                    if production == rhs:
                        return index + prod_index
        return -1

    def closure(self, items):
        closure_set = set(items)
        worklist = list(items)  # Use a worklist for efficiency
        
        while worklist:
            item = worklist.pop()
            lhs, rhs, dot, lookahead = item
            
            # Check if there's a non-terminal after the dot
            if dot < len(rhs):
                symbol = rhs[dot]
                
                # If it's a non-terminal, add its productions to the closure
                if symbol in self.non_terminals:
                    # Calculate FIRST of the part after the symbol
                    beta = rhs[dot+1:] if dot+1 < len(rhs) else []
                    
                    # For each production of the non-terminal
                    for prod in self.rules[symbol]:
                        # Calculate appropriate lookaheads
                        if beta:
                            # Calculate FIRST(beta lookahead)
                            first_of_beta = set()
                            all_have_epsilon = True
                            
                            for beta_symbol in beta:
                                if beta_symbol in self.terminals:
                                    first_of_beta.add(beta_symbol)
                                    all_have_epsilon = False
                                    break
                                else:  # Non-terminal
                                    first_beta_sym = self.first_sets[beta_symbol].copy()
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
    
    def goto(self, items, symbol):
        next_items = {(lhs, tuple(rhs), dot+1, lookahead) for lhs, rhs, dot, lookahead in items if dot < len(rhs) and rhs[dot] == symbol}
        return self.closure(next_items) if next_items else set()

    def lr1_items(self):
        """Generate LALR(1) items by merging LR(1) states with identical cores."""
        # First generate regular LR(1) items
        start_item = (self.start_symbol, tuple(self.rules[self.start_symbol][0]), 0, '$')
        c = [self.closure({start_item})]
        state_map = {frozenset(c[0]): 0}
        added = True
        
        # Generate all LR(1) states
        while added:
            added = False
            for state in c.copy():
                symbols = {sym for lhs, rhs, dot, _ in state if dot < len(rhs) for sym in (rhs[dot],)}
                for sym in symbols:
                    goto_state = self.goto(state, sym)
                    if goto_state and frozenset(goto_state) not in state_map:
                        state_map[frozenset(goto_state)] = len(c)
                        c.append(goto_state)
                        added = True
        
        # Now merge states with the same core
        result = {}
        self.core_to_state = {}  # Store as instance variable so it can be used in construct_parsing_tables
        
        # Helper function to get the core of an item (ignoring lookahead)
        def get_item_core(item):
            lhs, rhs, dot, _ = item
            return (lhs, rhs, dot)
        
        # Helper function to get the core of a state
        def get_state_core(state):
            return frozenset(get_item_core(item) for item in state)
        
        # Process each original LR(1) state
        for i, state in enumerate(c):
            state_core = get_state_core(state)
            
            if state_core in self.core_to_state:
                # Merge with existing state
                existing_state_idx = self.core_to_state[state_core]
                
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
                self.core_to_state[state_core] = len(result)
                result[len(result)] = state
        
        # Recalculate transitions for merged states
        transitions = {}
        for i, state in result.items():
            transitions[i] = {}
            symbols = {sym for lhs, rhs, dot, _ in state if dot < len(rhs) for sym in (rhs[dot],)}
            
            for sym in symbols:
                goto_result = self.goto(state, sym)
                goto_core = get_state_core(goto_result)
                
                if goto_core in self.core_to_state:
                    transitions[i][sym] = self.core_to_state[goto_core]
        
        # Store transitions for later use
        self.transitions = transitions
        
        return result

    def construct_parsing_tables(self, states=None):
        """
        Construct ACTION and GOTO tables based on the computed LR(1) or LALR(1) states.
        
        Args:
            states: The LR(1) or LALR(1) states (if None, uses self.lr1_items())
            
        Returns:
            Tuple of (action_table, goto_table, conflicts)
        """
        if states is None:
            states = self.lr1_items()
        
        # Initialize ACTION and GOTO tables
        action_table = {}
        goto_table = {}
        conflicts = []
        
        # Get all terminals and non-terminals
        all_terminals = self.terminals.copy()
        all_terminals.add('$')  # EOF marker
        all_non_terminals = self.non_terminals.copy()
        
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
                goto_state = self.goto(state, symbol)
                
                # Get the core of the goto state
                goto_core = frozenset((lhs, rhs, dot) for lhs, rhs, dot, _ in goto_state)
                
                if goto_state and goto_core in self.core_to_state:
                    next_state = self.core_to_state[goto_core]
                    
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
                    if lhs == self.start_symbol and dot == len(rhs) and lookahead == '$':
                        # Check if this is for the initial production of the start symbol
                        if len(rhs) == 1 and rhs[0] in self.non_terminals:
                            action_table[state_idx]['$'] = "accept"
                            continue
                    
                    # Regular reduce action
                    prod_num = self.get_production_number(lhs, list(rhs))
                    action = f"reduce {prod_num}"
                    
                    if lookahead in action_table[state_idx]:
                        register_conflict(state_idx, lookahead, action_table[state_idx][lookahead], action)
                    
                    action_table[state_idx][lookahead] = action
        
        return action_table, goto_table, conflicts

# Helper function to get the core of an item (ignoring lookahead)
def get_item_core(item):
    lhs, rhs, dot, _ = item
    return (lhs, rhs, dot)

# Helper function to get the core of a state
def get_state_core(state):
    return frozenset(get_item_core(item) for item in state)

# Add these methods to the Grammar class
Grammar.construct_parsing_tables = Grammar.construct_parsing_tables
Grammar.get_item_core = get_item_core
Grammar.get_state_core = get_state_core

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

# Update the main function to support multiple input parsing
if __name__ == "__main__":
    print("=== LALR(1) Parser Generator and String Parser ===")
    
    # Get grammar from user
    grammar_str = get_grammar_input()
    
    # Compute LALR(1) items
    print("\nCalculating LALR(1) items...")
    grammar = Grammar(grammar_str)
    lalr1_states = grammar.lr1_items()
    
    # Display the states
    print(f"\nGenerated {len(lalr1_states)} LALR(1) states")
    display_lr1_states(lalr1_states)
    
    # Construct parsing tables
    print("\nConstructing parsing tables...")
    action_table, goto_table, conflicts = grammar.construct_parsing_tables(lalr1_states)
    
    # Report conflicts if any
    if conflicts:
        print("\nConflicts detected:")
        for conflict in conflicts:
            print(f"  - {conflict}")
    else:
        print("\nNo conflicts detected.")
    
    # Display the parsing tables
    display_parsing_tables(action_table, goto_table, grammar.terminals, grammar.non_terminals)
    
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
    
    print("\nLALR(1) parsing session completed.")
