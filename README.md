# Compiler Design Project

This repository contains implementations of various parsing techniques and a simple SQL parser. Below is an overview of the implemented components:

## 1. LR(1) Parser
The LR(1) parser generates parsing tables for context-free grammars using the LR(1) parsing technique. It includes:
- **FIRST and FOLLOW sets computation**: Calculates the FIRST and FOLLOW sets for the grammar.
- **LR(1) Automaton Construction**: Builds the LR(1) automaton with states and transitions.
- **Parsing Table Generation**: Constructs the ACTION and GOTO tables.
- **Conflict Detection**: Identifies and reports shift-reduce or reduce-reduce conflicts.
- **Graphical Visualization**: Optionally visualizes the parsing table using `matplotlib`.

### Features:
- Interactive grammar input in BNF-like format.
- Graphical visualization of parsing tables (requires `matplotlib`).
- Input string testing to validate the grammar.

### Usage:
Run the script:
```bash
python3 lr1_parser_generator.py
```

## 2. LALR Parser
The LALR parser is an optimization of the LR(1) parser. It merges similar states in the LR(1) automaton to reduce the size of the parsing table while maintaining the same language recognition capability.

### Features:
- Efficient parsing table generation with reduced memory usage.
- Handles a subset of LR(1) grammars with fewer states.

### Usage:
The LALR parser is implemented in a similar structure to the LR(1) parser. Refer to the respective script for details.

## 3. Simple SQL Parser
A simple SQL parser is implemented to parse and validate basic SQL queries. It supports:
- SELECT statements with basic clauses like `WHERE`, `ORDER BY`, and `GROUP BY`.
- Syntax validation and error reporting.

### Features:
- Lightweight SQL parsing for educational purposes.
- Extendable for additional SQL features.

### Usage:
Refer to the SQL parser script for usage instructions.

## Requirements
- Python 3.x
- Optional: `matplotlib` for graphical visualization.

## How to Run
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Compiler_Design
   ```
2. Run the desired parser script:
   ```bash
   python3 <script_name>.py
   ```

