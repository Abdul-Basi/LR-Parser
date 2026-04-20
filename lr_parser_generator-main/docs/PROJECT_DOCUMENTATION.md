# LR Parser Studio: Detailed Project Documentation

Repository: [https://github.com/Abdul-Basi/LR-Parser.git](https://github.com/Abdul-Basi/LR-Parser.git)

## 1. Overview

LR Parser Studio is a Python-based interactive system for constructing and analyzing bottom-up parsers from user-defined context-free grammars.

The project combines:
- formal grammar processing
- multiple LR parser-generation strategies
- parsing table synthesis
- conflict diagnostics
- interactive visualization in Streamlit

It is intended for compiler-design learning, parser debugging, and grammar experimentation.

## 2. Goals and Scope

### 2.1 Primary goals
- Accept grammar definitions from users in a friendly format.
- Compute grammar properties (FIRST/FOLLOW).
- Build LR parser tables for four parser families.
- Simulate parser execution for token streams.
- Explain and export parser artifacts.

### 2.2 Supported parser families
- LR(0)
- SLR(1)
- LR(1)
- LALR(1)

### 2.3 Out of scope
- Full lexical analysis/tokenization pipeline
- Error recovery algorithms beyond reporting
- Grammar optimization passes (left factoring/elimination automation)

## 3. High-Level Architecture

The codebase follows a modular layered design:

1. Grammar layer
- Defines generic grammar structures.
- Computes FIRST and FOLLOW sets.

2. Item layer
- Represents LR(0) and LR(1) items.

3. Parser layer
- Contains abstract parser behavior and family-specific parser constructors.
- Produces ACTION/GOTO tables and parser transitions.

4. UI layer
- Collects user grammar input.
- Builds selected parser.
- Visualizes and exports parser artifacts.

5. Test layer
- Verifies grammar logic, item behavior, parser behavior, and UI helper utilities.

## 4. Module-by-Module Reference

## 4.1 Entry point

File: run.py
- Imports run_ui from the UI module.
- Starts the Streamlit application workflow.

## 4.2 Grammar modules

### grammar.py
Defines the base Grammar class with:
- terminals
- non_terminals
- productions
- start_symbol

Key behavior:
- Grammar augmentation using S' -> S
- Production numbering for reduce-action references

### context_free_grammar.py
Extends Grammar with:
- FIRST set computation
- FOLLOW set computation

Key points:
- FIRST initialized for declared non-terminals and terminals.
- FOLLOW initialized for non-terminals; start symbol includes $.
- Iterative fixed-point updates are used in both algorithms.

## 4.3 Item modules

### lr0_item.py
Represents LR(0) item (lhs, rhs, dot_position):
- Hashable and comparable
- String representation with dot marker

### lr1_item.py
Extends LR(0) item with lookahead set:
- Lookahead-aware hashing/equality
- LR(1)-style printable representation

## 4.4 Parser modules

### lr_parser.py (abstract base)
Responsibilities:
- Grammar augmentation and FIRST initialization
- Shared parser state containers:
  - action
  - goto_table
  - states
  - transitions
  - C (canonical collection)
  - conflicts
- Generic parse() simulator
- Conflict-aware action insertion helper (_set_action)

Conflict model:
- If an ACTION cell is already populated with a different action, conflict data is recorded.
- Existing action is preserved; incoming action is tracked for diagnostics.

### lr0_parser.py
Implements:
- closure(items)
- goto(items, symbol)
- canonical item collection generation
- LR(0) parsing-table construction

Reduce actions are applied over all terminals + $.

### slr1_parser.py
Extends LR(0) behavior:
- Uses FOLLOW(lhs) to limit reduce actions.

This reduces conflicts compared to LR(0) for many grammars.

### lr1_parser.py
Implements full LR(1):
- LR(1) closure with lookahead propagation
- FIRST(beta a) style lookahead computation for items
- LR(1)-specific ACTION generation using item lookaheads

### lalr1_parser.py
Extends LR(1):
- Merges LR(1) states that share the same LR(0) core.
- Unions lookahead sets during merge.
- Recomputes transitions over merged states.

This reduces table size while preserving most LR(1) precision.

## 4.5 UI module

File: src/ui/app.py

Major capabilities:
- Custom visual theme and responsive layout
- Grammar presets
- Preset loading into sidebar input state
- Grammar parsing and normalization
- Missing-symbol inference from productions
- Parser selection and build flow
- Feature explorer with table/collection visualization
- CSV export utilities
- Conflict report with explanations and suggested refactors

Main helper groups:

Input processing:
- _split_symbols
- _parse_productions
- _infer_missing_symbols

Preset workflow:
- _get_grammar_presets
- _apply_grammar_preset

Export builders:
- _build_transition_table
- _build_canonical_collection_table
- _build_conflicts_table

Conflict guidance:
- _explain_conflict

## 5. End-to-End User Workflow

1. User enters grammar or loads a preset.
2. App validates and parses productions.
3. App infers missing symbols and constructs a ContextFreeGrammar.
4. User selects parser family and builds parser.
5. Parser generates canonical states + parsing tables.
6. User inspects selected feature view.
7. User can export artifacts as CSV.
8. User can parse token strings and inspect configuration steps.

## 6. Data Structures and Contracts

### 6.1 Productions
- Stored as tuples: (lhs, rhs_list)
- Example: ("E", ["T", "E2"])

### 6.2 ACTION table
- Dictionary keyed by (state:int, terminal:str)
- Values:
  - ('shift', next_state)
  - ('reduce', lhs, rhs)
  - ('accept',)

### 6.3 GOTO table
- Dictionary keyed by (state:int, non_terminal:str)
- Value: next_state:int

### 6.4 Conflicts
Each conflict record includes:
- state
- symbol
- existing_action
- incoming_action
- conflict_type

## 7. Algorithms Summary

## 7.1 FIRST computation
Iterative fixed-point algorithm:
- FIRST(terminal) initialized with itself.
- FIRST(lhs) updated from RHS symbols.
- Epsilon propagation handled across symbol chain.

## 7.2 FOLLOW computation
Iterative right-to-left trailer propagation:
- FOLLOW(start) includes $.
- For each production, trailer set moves across RHS.
- FIRST-based epsilon behavior updates trailer.

## 7.3 Canonical collection
For each parser family:
- Start from augmented item.
- Use closure + goto transitions.
- Discover reachable item sets with BFS/queue-like traversal.

## 7.4 Parse simulation
- Initialize stack with state 0.
- Read ACTION(state, token).
- Execute shift/reduce/accept until completion or failure.
- Record each configuration for UI display.

## 8. Exports and Reporting

CSV export is available for:
- Canonical collection
- ACTION table
- GOTO table
- Conflicts report

Conflict report includes:
- raw conflict facts
- natural-language explanation
- grammar refactor suggestion

Special handling exists for dangling-else style shift-reduce patterns.

## 9. Testing Strategy

Testing is organized by subsystem:

1. grammars/
- FIRST/FOLLOW correctness
- augmentation behavior

2. items/
- representation/equality/hash behavior for LR items

3. parsers/
- canonical collection construction
- ACTION/GOTO formation
- parse acceptance/rejection paths
- conflict tracking helper behavior

4. ui/
- input parsing helpers
- symbol inference
- export table shaping
- preset utilities

Suggested commands:

Run full suite:
```bash
pytest
```

Run focused UI suite:
```bash
pytest tests/ui/test_app_helpers.py tests/ui/test_table_exports.py
```

## 10. Limitations and Known Considerations

- Input parsing expects whitespace-separated tokens in production RHS.
- No integrated lexer; user supplies tokenized input for parse simulation.
- Conflict explanation is rule-based and heuristic, not proof-minimal.
- Large grammars may produce large DataFrames and slower UI rendering.

## 11. Extension Guide

Recommended next extensions:
- Parse-step CSV export
- User-defined preset persistence to JSON
- Inline conflict highlighting inside ACTION table cells
- Guided error recovery with expected-token hints
- More compact mobile table rendering mode

## 12. Practical Usage Notes

- For expression grammars, prefer E/T/F factorization to reduce shift-reduce conflicts.
- Use LR(1) when ambiguous cases require strongest lookahead precision.
- Use LALR(1) when state-count reduction is desired with near LR(1) power.
- Use Conflicts Report early when grammar edits produce unstable tables.

## 13. Versioning and Maintenance Suggestions

- Keep parser-family behavior changes behind targeted tests.
- Add regression cases for every grammar conflict discovered during usage.
- Preserve helper-function tests when adjusting UI workflows.
- Document new presets and export formats in README and this file together.
