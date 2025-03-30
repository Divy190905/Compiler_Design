from collections import defaultdict

def parse_grammar(grammar_str):
    rules = {}
    for line in grammar_str.strip().split("\n"):
        lhs, rhs = line.split("->")
        lhs = lhs.strip()
        productions = [prod.strip().split() for prod in rhs.split("|")]
        rules[lhs] = productions
    return rules

class Grammar:
    def __init__(self, grammar_str):
        self.rules = parse_grammar(grammar_str)
        self.start_symbol = list(self.rules.keys())[0]
        self.terminals, self.non_terminals = self.get_symbols()
        self.first_sets = self.compute_first_sets()

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

    def closure(self, items):
        closure_set = set(items)
        added = True
        
        while added:
            added = False
            new_items = set()
            
            for lhs, rhs, dot, lookahead in closure_set:
                if dot < len(rhs):
                    symbol = rhs[dot]
                    if symbol in self.non_terminals:
                        for prod in self.rules[symbol]:
                            for term in self.first_sets[rhs[dot+1]] if dot+1 < len(rhs) else {lookahead}:
                                new_item = (symbol, tuple(prod), 0, term)
                                if new_item not in closure_set:
                                    new_items.add(new_item)
                                    added = True
            closure_set |= new_items
        return closure_set
    
    def goto(self, items, symbol):
        next_items = {(lhs, tuple(rhs), dot+1, lookahead) for lhs, rhs, dot, lookahead in items if dot < len(rhs) and rhs[dot] == symbol}
        return self.closure(next_items) if next_items else set()

    def lr1_items(self):
        start_item = (self.start_symbol, tuple(self.rules[self.start_symbol][0]), 0, '$')
        c = [self.closure({start_item})]
        state_map = {frozenset(c[0]): 0}
        added = True
        
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
        
        return {i: state for i, state in enumerate(c)}

# Function to generate LR(1) states from grammar string
def generate_lr1_states(grammar_str):
    grammar = Grammar(grammar_str)
    return grammar.lr1_items()

# Example usage
grammar_str = """
S' -> S
S -> A A
A -> a A | b
"""

lr1_states = generate_lr1_states(grammar_str)

for state, items in lr1_states.items():
    print(f"State {state}:")
    for item in sorted(items):
        lhs, rhs, dot, lookahead = item
        rhs_str = " ".join(list(rhs[:dot]) + ["•"] + list(rhs[dot:]))
        print(f"  {lhs} -> {rhs_str}, {lookahead}")
