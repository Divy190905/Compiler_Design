# LR(1) Parsing Table Generator

This is a Python program that generates LR(1) parsing tables for context-free grammars. The program takes a grammar as input, computes the necessary automaton and constructs ACTION and GOTO tables.

## Features

- Accepts grammar input in BNF-like format
- Automatically augments the grammar
- Computes FIRST and FOLLOW sets for non-terminals
- Constructs the canonical collection of LR(1) items
- Generates ACTION and GOTO tables
- Detects and reports shift-reduce and reduce-reduce conflicts
- Displays the parsing table in a readable format

## Requirements

- Python 3.6+
- Pandas (optional, for better table visualization)

## Usage

Run the main script:

```bash
python3 lr1_parser_generator.py
```

Then, input your grammar in BNF-like format. For example:

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

The program will output:
- The augmented grammar
- FIRST and FOLLOW sets
- Number of states in the LR(1) automaton
- Any detected conflicts
- The LR(1) parsing table

## Example Grammar

Here's an example grammar you can try:

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

## Project Structure

- `lr1_parser_generator.py`: Main script
- `grammar.py`: Grammar representation and parsing
- `first_follow.py`: FIRST and FOLLOW set computation
- `lr1_items.py`: LR(1) items and automaton construction
- `parsing_table.py`: ACTION and GOTO table generation
- `visualizer.py`: Table visualization

## How It Works

1. The grammar is parsed and augmented with a new start symbol.
2. FIRST and FOLLOW sets are computed for all non-terminals.
3. The canonical collection of LR(1) items is constructed:
   - LR(1) items are represented as `(A → α•β, a)` where `a` is the lookahead.
   - Closure and goto operations are used to build the state machine.
4. ACTION and GOTO tables are generated based on the automaton.
5. Conflicts (shift-reduce, reduce-reduce) are detected and reported.
6. The parsing table is displayed in a readable format.

## References

- Compilers: Principles, Techniques, and Tools (Dragon Book)
- Engineering a Compiler
