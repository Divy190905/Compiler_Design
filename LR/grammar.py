"""
Grammar module for the LR(1) parsing table generator.

This module contains the Grammar class that handles the storage, parsing,
and manipulation of context-free grammars.
"""

class Grammar:
    """Represents a context-free grammar."""
    
    def __init__(self, grammar_str):
        """
        Initialize Grammar from a string representation.
        
        Args:
            grammar_str (str): String containing grammar rules in BNF-like format
                              e.g., "S -> A B | C\nA -> a\nB -> b\nC -> c"
        """
        self.productions = []  # List of (lhs, rhs) tuples where rhs is a tuple of symbols
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None
        self.epsilon = 'ε'  # Epsilon symbol
        
        # Parse the grammar
        self._parse_grammar(grammar_str)
        
        # Augment the grammar
        self._augment_grammar()
    
    def _parse_grammar(self, grammar_str):
        """Parse a grammar string into internal representation."""
        lines = [line.strip() for line in grammar_str.strip().split('\n')]
        lines = [line for line in lines if line and not line.startswith('#')]
        
        for i, line in enumerate(lines):
            if '->' not in line:
                raise ValueError(f"Line {i+1}: Missing production arrow (->): {line}")
            
            lhs, rhs_str = line.split('->', 1)
            lhs = lhs.strip()
            
            if not lhs:
                raise ValueError(f"Line {i+1}: Empty left-hand side: {line}")
            
            self.non_terminals.add(lhs)
            
            if lhs in self.terminals:
                self.terminals.remove(lhs)  # Remove from terminals if it was added by mistake
                
            # If this is the first production, set the start symbol
            if self.start_symbol is None:
                self.start_symbol = lhs
            
            # Split alternatives
            alternatives = [alt.strip() for alt in rhs_str.split('|')]
            
            for alt in alternatives:
                # Handle empty productions (epsilon)
                if not alt:
                    self.productions.append((lhs, (self.epsilon,)))
                    continue
                
                # Split into symbols
                symbols = tuple(sym.strip() for sym in alt.split())
                
                # Add the production
                self.productions.append((lhs, symbols))
                
                # Add symbols to terminals set (if not in non_terminals)
                for symbol in symbols:
                    if symbol != self.epsilon and symbol not in self.non_terminals:
                        self.terminals.add(symbol)
    
    def _augment_grammar(self):
        """
        Augment the grammar by adding a new start production S' -> S
        where S is the original start symbol.
        """
        if not self.start_symbol:
            raise ValueError("Cannot augment grammar: no start symbol defined")
        
        new_start = f"{self.start_symbol}'"
        # Ensure new_start is not already in the grammar
        while new_start in self.non_terminals:
            new_start += "'"
        
        self.non_terminals.add(new_start)
        # Insert at the beginning to prioritize the augmented start rule
        self.productions.insert(0, (new_start, (self.start_symbol,)))
        self.start_symbol = new_start
    
    def get_productions_for(self, non_terminal):
        """Get all productions for a given non-terminal."""
        return [(lhs, rhs) for lhs, rhs in self.productions if lhs == non_terminal]
    
    def get_production_number(self, lhs, rhs):
        """Get the production number for a given production."""
        production = (lhs, rhs)
        try:
            return self.productions.index(production)
        except ValueError:
            return -1
    
    def __str__(self):
        """Return string representation of the grammar."""
        result = []
        for lhs, rhs in self.productions:
            rhs_str = ' '.join(rhs)
            result.append(f"{lhs} -> {rhs_str}")
        return '\n'.join(result)
    
    def parse_input(self, input_string, action_table, goto_table):
        """
        Parse an input string using LR(1) parsing tables to check if it's valid.
        
        Args:
            input_string (str): The string to parse (space-separated tokens)
            action_table (dict): ACTION table from construct_parsing_table
            goto_table (dict): GOTO table from construct_parsing_table
            
        Returns:
            tuple: (is_valid, steps, error_message)
        """
        # Tokenize the input
        tokens = input_string.split() + ['$']  # Add the end marker
        
        # Initialize parsing stack with state 0
        stack = [0]
        
        # List to store parsing steps for debugging
        steps = []
        
        # Current position in the input
        position = 0
        
        while True:
            state = stack[-1]
            symbol = tokens[position]
            
            # Record the current step
            steps.append({
                'stack': stack.copy(),
                'input': tokens[position:],
                'action': None
            })
            
            # Look up the action
            if (state, symbol) not in action_table:
                error_msg = f"No action defined for state {state} on symbol '{symbol}'"
                steps[-1]['action'] = f"ERROR: {error_msg}"
                return False, steps, error_msg
            
            # Get the action
            action = action_table[(state, symbol)]
            steps[-1]['action'] = action
            
            # Perform the action
            if action[0] == 'shift':
                # Shift action
                next_state = action[1]
                stack.append(symbol)
                stack.append(next_state)
                position += 1
                
            elif action[0] == 'reduce':
                # Reduce action
                production_num = action[1]
                lhs, rhs = self.productions[production_num]
                
                # Pop 2 * |rhs| items from the stack
                for _ in range(2 * len(rhs)):
                    stack.pop()
                
                # Get the current state
                state = stack[-1]
                
                # Push the non-terminal
                stack.append(lhs)
                
                # Look up the goto
                if (state, lhs) not in goto_table:
                    error_msg = f"No goto defined for state {state} on non-terminal {lhs}"
                    steps[-1]['action'] = f"ERROR: {error_msg}"
                    return False, steps, error_msg
                
                # Push the new state
                next_state = goto_table[(state, lhs)]
                stack.append(next_state)
                
            elif action[0] == 'accept':
                # Parsing successful
                steps[-1]['action'] = "ACCEPT"
                return True, steps, None
                
            else:
                # Invalid action
                error_msg = f"Invalid action {action} in state {state} on symbol {symbol}"
                steps[-1]['action'] = f"ERROR: {error_msg}"
                return False, steps, error_msg
        
        # This line should never be reached
        return False, steps, "Unexpected end of parsing"

    def test_input(self, input_str, action_table, goto_table, verbose=False, collect_steps=False):
        """
        Test if an input string is accepted by the LR(1) parser.
        
        Args:
            input_str (str): Input string to test
            action_table (dict): ACTION table for the parser
            goto_table (dict): GOTO table for the parser
            verbose (bool): Whether to print parsing steps
            collect_steps (bool): Whether to collect parsing steps for visualization
        
        Returns:
            tuple: (is_valid, error_message, parsing_steps)
        """
        # Tokenize the input
        tokens = input_str.split()
        tokens.append('$')  # End marker
        
        # Initialize stack with initial state
        stack = [0]
        input_index = 0
        steps = []
        
        while True:
            state = stack[-1]
            symbol = tokens[input_index] if input_index < len(tokens) else '$'
            
            # Look up action
            action = action_table.get((state, symbol))
            
            # Format stack and input for display
            stack_str = ' '.join(map(str, stack))
            input_str = ' '.join(tokens[input_index:])
            
            if collect_steps:
                steps.append({
                    'stack': stack_str,
                    'input': input_str,
                    'action': action if action else "ERROR"
                })
            
            if verbose:
                print(f"Stack: {stack_str}")
                print(f"Input: {input_str}")
                print(f"Action: {action}")
                print()
            
            # Process action
            if action is None:
                error_msg = f"No action defined for state {state} on symbol '{symbol}'"
                return False, error_msg, steps
            
            if action[0] == 'shift':
                stack.append(symbol)
                stack.append(action[1])
                input_index += 1
            elif action[0] == 'reduce':
                production_index = action[1]
                lhs, rhs = self.productions[production_index]
                
                # Pop 2 * |rhs| items from the stack
                for _ in range(2 * len(rhs)):
                    stack.pop()
                
                # Get new state from GOTO table
                goto_state = goto_table.get((stack[-1], lhs))
                
                # Push LHS and new state
                stack.append(lhs)
                stack.append(goto_state)
            elif action[0] == 'accept':
                if collect_steps:
                    steps[-1]['action'] = "ACCEPT"
                return True, None, steps
                
        return False, "Unknown error", steps
