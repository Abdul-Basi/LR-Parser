# LR Parser Studio

An interactive educational and practical toolkit for building and exploring LR-family parsers.

The application supports LR(0), SLR(1), LALR(1), and LR(1) workflows with an interface designed for grammar experimentation, parser-table inspection, conflict analysis, and exportable results.

## Highlights

- Grammar creation from user input with symbol normalization and auto-inference.
- Built-in grammar presets for quick demos and learning sessions.
- Parser generation for LR(0), SLR(1), LALR(1), and LR(1).
- Deep parser introspection:
   - augmented grammar
   - FIRST and FOLLOW sets
   - canonical item collections
   - ACTION and GOTO tables
- Conflict tracking with explanations and refactor suggestions.
- CSV exports for canonical collections, ACTION tables, GOTO tables, and conflict reports.
- Token-by-token parse simulation with visible stack/action trace.
- Modern Streamlit UI with responsive layout and summary metrics.

## Tech Stack

- Python 3.11+
- Streamlit
- Pandas
- Pytest

## Project Layout

```text
run.py
src/
   grammars/
      grammar.py
      context_free_grammar.py
   items/
      lr0_item.py
      lr1_item.py
   parsers/
      lr_parser.py
      lr0_parser.py
      slr1_parser.py
      lalr1_parser.py
      lr1_parser.py
   ui/
      app.py
tests/
   grammars/
   items/
   parsers/
   ui/
```

## Repository

Project source: [https://github.com/Abdul-Basi/LR-Parser.git](https://github.com/Abdul-Basi/LR-Parser.git)

## Setup

1. Open a terminal in the project root.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
python -m streamlit run run.py
```

After startup, open the local URL shown by Streamlit (typically http://localhost:8501).

## Quick Start

1. Select a grammar preset in the sidebar or enter a custom grammar.
2. Click Define Grammar.
3. Choose parser type (LR(0), SLR(1), LALR(1), LR(1)).
4. Click Build Parser.
5. Explore sections in Parser Explorer:
    - Augmented Grammar
    - FIRST Sets
    - FOLLOW Sets
    - Canonical Collection of Items
    - ACTION Table
    - GOTO Table
    - Conflicts Report
    - Parse Input String
6. Export generated tables as CSV when needed.

## Testing

Run all tests:

```bash
pytest
```

Run focused UI helper tests:

```bash
pytest tests/ui/test_app_helpers.py tests/ui/test_table_exports.py
```

## Documentation

Detailed technical documentation is available in [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md).

## Roadmap

- Parse-step CSV export.
- Additional parser diagnostics and guided error recovery.
- Enhanced mobile ergonomics for large tables.
- Custom user-defined preset persistence.

