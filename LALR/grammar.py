"""
Grammar module for LR parser generator.

This module contains the Grammar class and related functionality for
parsing grammar input and computing FIRST sets.
"""

from collections import defaultdict

def parse_grammar_input(grammar_str):
    """Parse grammar input string into a dictionary of rules."""
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

class Grammar:
    def __init__(self, grammar_str):
        self.rules = parse_grammar_input(grammar_str)
        self.start_symbol = list(self.rules.keys())[0]
        self.terminals, self.non_terminals = self.get_symbols()
        self.first_sets = self.compute_first_sets()
        self.epsilon = ''  # Define epsilon for this grammar

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