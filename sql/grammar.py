"""
Grammar module for LR parser generator.

This module contains the Grammar class and related functionality for
parsing grammar input and computing FIRST sets.
"""

from collections import defaultdict

def parse_grammar_input(grammar_input):
    """
    Parse the grammar input to extract production rules.
    """
    rules = []
    lines = grammar_input.strip().split('\n')
    
    for line in lines:
        # Skip empty lines
        line = line.strip()
        if not line:
            continue
        
        # Skip comment lines
        if line.startswith('#'):
            continue
            
        # Parse the rule
        lhs, rhs = line.split("->")
        lhs = lhs.strip()
        rhs = rhs.strip()
        
        # Add the rule
        rules.append((lhs, rhs))
    
    return rules

class Grammar:
    def __init__(self, grammar_str):
        # Get raw rules as list of (lhs, rhs) tuples
        raw_rules = parse_grammar_input(grammar_str)
        
        # Convert to dictionary format expected by the rest of the code
        self.rules = defaultdict(list)
        for lhs, rhs in raw_rules:
            # Split the right side by '|' if it contains alternatives
            if '|' in rhs:
                alternatives = [alt.strip() for alt in rhs.split('|')]
                for alt in alternatives:
                    self.rules[lhs].append(alt.split())
            else:
                self.rules[lhs].append(rhs.split())
        
        # Get the start symbol (first non-terminal in the grammar)
        self.start_symbol = next(iter(self.rules.keys()))
        
        # Extract terminals and non-terminals
        self.terminals, self.non_terminals = self.get_symbols()
        
        # Compute FIRST sets
        self.first_sets = self.compute_first_sets()
        
        # Define epsilon for this grammar
        self.epsilon = ''

    def get_symbols(self):
        """Identify terminal and non-terminal symbols in the grammar."""
        terminals, non_terminals = set(), set(self.rules.keys())
        for rhs in self.rules.values():
            for prod in rhs:
                for symbol in prod:
                    if symbol not in non_terminals:
                        terminals.add(symbol)
        return terminals, non_terminals

    def compute_first_sets(self):
        """Compute FIRST sets for all symbols in the grammar."""
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
        """Get the production number for a given rule."""
        prod_count = 0
        for nt, productions in self.rules.items():
            for prod in productions:
                if nt == lhs and prod == rhs:
                    return prod_count
                prod_count += 1
        return -1

    def get_productions_for(self, non_terminal):
        """Return all productions for a given non-terminal."""
        result = []
        if non_terminal in self.rules:
            for production in self.rules[non_terminal]:
                result.append((non_terminal, tuple(production)))
        return result
