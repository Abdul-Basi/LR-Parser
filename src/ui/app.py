import streamlit as st
import pandas as pd

from src.grammars.context_free_grammar import ContextFreeGrammar
from src.parsers.lalr1_parser import LALR1Parser
from src.parsers.lr0_parser import LR0Parser
from src.parsers.lr1_parser import LR1Parser
from src.parsers.slr1_parser import SLR1Parser


def _inject_custom_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap');
            :root {
                --bg-soft: #f7f4ec;
                --ink: #1f1f1f;
                --accent: #005f73;
                --accent-2: #9b2226;
                --card: #fffdf8;
                --border: #e3d9c9;
            }
            .stApp {
                background:
                    radial-gradient(circle at 20% 0%, #fff8e8 0%, rgba(255, 248, 232, 0) 45%),
                    radial-gradient(circle at 100% 25%, #d7f0eb 0%, rgba(215, 240, 235, 0) 40%),
                    var(--bg-soft);
                color: var(--ink);
                font-family: 'Source Sans 3', sans-serif;
            }
            h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.02em; }
            [data-testid="stSidebar"] { border-right: 1px solid var(--border); background: #fffaf0; }
            .hero-block {
                background: linear-gradient(135deg, #005f73 0%, #0a9396 45%, #94d2bd 100%);
                border-radius: 14px;
                padding: 1.25rem 1.5rem;
                margin-bottom: 1rem;
                color: #ffffff;
                box-shadow: 0 8px 24px rgba(0, 95, 115, 0.22);
            }
            .hero-title { margin: 0; font-size: 1.7rem; font-weight: 700; }
            .hero-subtitle { margin-top: 0.35rem; font-size: 1rem; opacity: 0.95; }
            .section-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.05rem;
                font-weight: 700;
                color: var(--accent);
                margin-top: 0.25rem;
                margin-bottom: 0.35rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }
            [data-testid="stMetric"] {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 0.45rem 0.7rem;
                box-shadow: 0 2px 10px rgba(20, 20, 20, 0.06);
            }
            .stButton > button {
                border-radius: 10px;
                border: 1px solid #004e60;
                background: linear-gradient(180deg, #0a7f93 0%, #005f73 100%);
                color: #ffffff;
                font-weight: 600;
            }
            .stDownloadButton > button {
                border-radius: 10px;
                border: 1px solid #8c1c20;
                background: linear-gradient(180deg, #bc4749 0%, #9b2226 100%);
                color: #ffffff;
                font-weight: 600;
            }
            @media (max-width: 900px) {
                .hero-title { font-size: 1.35rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _get_grammar_presets() -> dict[str, dict[str, str]]:
    return {
        "Arithmetic Expressions": {
            "non_terminals": "E, T, F, E2, T2",
            "terminals": "id, +, *, (, )",
            "start_symbol": "E",
            "productions": "\n".join([
                "E -> T E2",
                "E2 -> + T E2 | ε",
                "T -> F T2",
                "T2 -> * F T2 | ε",
                "F -> ( E ) | id",
            ]),
        },
        "Simple Assignment": {
            "non_terminals": "S, A, E",
            "terminals": "id, :=, +, num",
            "start_symbol": "S",
            "productions": "\n".join([
                "S -> A",
                "A -> id := E",
                "E -> E + num | num",
            ]),
        },
        "If Else (Dangling Else)": {
            "non_terminals": "S, L",
            "terminals": "if, then, else, id",
            "start_symbol": "S",
            "productions": "\n".join([
                "S -> if id then S L | id",
                "L -> else S | ε",
            ]),
        },
    }


def _apply_grammar_preset(session_state: dict, preset_name: str, presets: dict[str, dict[str, str]]) -> bool:
    if preset_name == "Custom" or preset_name not in presets:
        return False
    preset = presets[preset_name]
    session_state["non_terminals_input"] = preset["non_terminals"]
    session_state["terminals_input"] = preset["terminals"]
    session_state["start_symbol_input"] = preset["start_symbol"]
    session_state["productions_input"] = preset["productions"]
    return True


def _split_symbols(raw_value: str) -> list[str]:
    return [symbol.strip() for symbol in raw_value.replace(',', ' ').split() if symbol.strip()]


def _parse_productions(productions_text: str) -> tuple[list[tuple[str, list[str]]], set[str], set[str]]:
    productions_list = []
    lhs_symbols = set()
    rhs_symbols = set()
    for line in productions_text.splitlines():
        if '->' not in line:
            raise ValueError(f"Invalid production format: {line}")
        lhs, rhs = line.split('->', 1)
        lhs = lhs.strip()
        rhs = rhs.strip()
        lhs_symbols.add(lhs)
        for alt in rhs.split('|'):
            prod_rhs = alt.strip().split()
            rhs_symbols.update(prod_rhs)
            productions_list.append((lhs, prod_rhs))
    return productions_list, lhs_symbols, rhs_symbols


def _infer_missing_symbols(
    non_terminals_list: list[str],
    terminals_list: list[str],
    productions_list: list[tuple[str, list[str]]],
) -> tuple[list[str], list[str], list[str], list[str]]:
    lhs_symbols = {lhs for lhs, _ in productions_list}
    rhs_symbols = {symbol for _, rhs in productions_list for symbol in rhs}
    declared_non_terminals = set(non_terminals_list)
    declared_terminals = set(terminals_list)
    inferred_non_terminals = sorted(lhs_symbols - declared_non_terminals - {'ε'})
    resolved_non_terminals = declared_non_terminals | set(inferred_non_terminals)
    inferred_terminals = sorted(
        symbol for symbol in rhs_symbols
        if symbol not in resolved_non_terminals and symbol not in declared_terminals and symbol != 'ε'
    )
    updated_non_terminals = non_terminals_list[:]
    updated_terminals = terminals_list[:]
    for symbol in inferred_non_terminals:
        if symbol not in updated_non_terminals:
            updated_non_terminals.append(symbol)
    for symbol in inferred_terminals:
        if symbol not in updated_terminals:
            updated_terminals.append(symbol)
    return updated_non_terminals, updated_terminals, inferred_non_terminals, inferred_terminals


def _build_transition_table(mapping: dict[tuple[int, str], object], index_name: str) -> pd.DataFrame:
    table_data = {}
    for (state, symbol), value in mapping.items():
        table_data.setdefault(state, {})[symbol] = str(value)
    table = pd.DataFrame(table_data).T
    table.index.name = index_name
    return table


def _build_canonical_collection_table(collection: list[set[object]]) -> pd.DataFrame:
    rows = []
    for index, item_set in enumerate(collection):
        for item in sorted(item_set, key=str):
            rows.append({"State": f"I{index}", "Item": str(item)})
    return pd.DataFrame(rows, columns=["State", "Item"])


def _explain_conflict(conflict: dict[str, object]) -> tuple[str, str]:
    conflict_type = str(conflict.get("conflict_type", "unknown"))
    symbol = str(conflict.get("symbol", ""))
    existing_action = str(conflict.get("existing_action", ""))
    incoming_action = str(conflict.get("incoming_action", ""))
    explanation = (
        f"Parser state has competing actions on symbol '{symbol}': existing {existing_action} and incoming {incoming_action}."
    )
    if conflict_type in {"shift-reduce", "reduce-shift"}:
        if symbol == "else":
            suggestion = (
                "Likely dangling-else pattern. Split matched/unmatched statement non-terminals or associate else with the nearest if."
            )
        else:
            suggestion = (
                "Reduce grammar ambiguity by encoding precedence and associativity using helper non-terminals such as E/T/F."
            )
    elif conflict_type == "reduce-reduce":
        suggestion = (
            "Two reductions compete on the same lookahead. Refactor overlapping productions or split shared prefixes into distinct non-terminals."
        )
    else:
        suggestion = (
            "Review the productions reaching this state and separate ambiguous alternatives with clearer non-terminals or precedence structure."
        )
    return explanation, suggestion


def _build_conflicts_table(conflicts: list[dict[str, object]]) -> pd.DataFrame:
    rows = []
    for conflict in conflicts:
        explanation, suggestion = _explain_conflict(conflict)
        rows.append({
            "State": conflict["state"],
            "Symbol": conflict["symbol"],
            "Conflict Type": conflict["conflict_type"],
            "Existing Action": str(conflict["existing_action"]),
            "Incoming Action": str(conflict["incoming_action"]),
            "Explanation": explanation,
            "Suggested Refactor": suggestion,
        })
    return pd.DataFrame(rows, columns=["State", "Symbol", "Conflict Type", "Existing Action", "Incoming Action", "Explanation", "Suggested Refactor"])


def run_ui() -> None:
    st.set_page_config(page_title="LR Parser Generator", layout="wide", initial_sidebar_state="expanded")
    _inject_custom_styles()
    st.markdown(
        """
        <div class="hero-block">
            <p class="hero-title">LR Parser Studio</p>
            <p class="hero-subtitle">Design grammars, build LR families, inspect parser internals, and export artifacts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    presets = _get_grammar_presets()
    st.session_state.setdefault("selected_preset", "Custom")
    st.session_state.setdefault("non_terminals_input", "")
    st.session_state.setdefault("terminals_input", "")
    st.session_state.setdefault("start_symbol_input", "")
    st.session_state.setdefault("productions_input", "")

    st.sidebar.header("Grammar Definition")
    st.sidebar.caption("Use presets or define your own grammar and parser workflow.")
    preset_options = ["Custom"] + sorted(presets.keys())
    selected_preset = st.sidebar.selectbox(
        "Grammar Presets", preset_options,
        index=preset_options.index(st.session_state["selected_preset"]) if st.session_state["selected_preset"] in preset_options else 0,
        key="selected_preset",
    )
    if st.sidebar.button("Load Preset"):
        if _apply_grammar_preset(st.session_state, selected_preset, presets):
            st.sidebar.success(f"Loaded preset: {selected_preset}")

    non_terminals = st.sidebar.text_input("Enter non-terminals (space or comma-separated):", key="non_terminals_input")
    terminals = st.sidebar.text_input("Enter terminals (space or comma-separated):", key="terminals_input")
    start_symbol = st.sidebar.text_input("Enter the start symbol:", key="start_symbol_input")
    st.sidebar.subheader("Productions")
    st.sidebar.write("Use '->' to separate LHS and RHS, and '|' for alternatives.")
    productions = st.sidebar.text_area("Enter productions (one per line):", key="productions_input")

    if st.sidebar.button("Define Grammar"):
        if not all([non_terminals, terminals, start_symbol, productions]):
            st.error("Please complete all grammar fields.")
        else:
            try:
                non_terminals_list = _split_symbols(non_terminals)
                terminals_list = _split_symbols(terminals)
                productions_list, _, _ = _parse_productions(productions)
            except ValueError as error:
                st.error(str(error))
                return
            non_terminals_list, terminals_list, inferred_non_terminals, inferred_terminals = _infer_missing_symbols(
                non_terminals_list, terminals_list, productions_list
            )
            if start_symbol not in non_terminals_list:
                non_terminals_list.insert(0, start_symbol)
            grammar = ContextFreeGrammar(terminals_list, non_terminals_list, productions_list, start_symbol)
            st.session_state['grammar'] = grammar
            if inferred_non_terminals or inferred_terminals:
                inferred_message = []
                if inferred_non_terminals:
                    inferred_message.append(f"non-terminals: {', '.join(inferred_non_terminals)}")
                if inferred_terminals:
                    inferred_message.append(f"terminals: {', '.join(inferred_terminals)}")
                st.info("Inferred missing symbols from productions: " + "; ".join(inferred_message))
            st.success("Grammar defined successfully!")

    if 'grammar' in st.session_state:
        grammar = st.session_state['grammar']
        st.markdown("<div class='section-title'>Parser Builder</div>", unsafe_allow_html=True)
        parser_type = st.selectbox("Choose a parser type:", ["LR(0)", "SLR(1)", "LALR(1)", "LR(1)"])
        if st.button("Build Parser"):
            if parser_type == "LR(0)":
                parser = LR0Parser(grammar)
            elif parser_type == "SLR(1)":
                parser = SLR1Parser(grammar)
            elif parser_type == "LALR(1)":
                parser = LALR1Parser(grammar)
            else:
                parser = LR1Parser(grammar)
            parser.items()
            parser.construct_parsing_table()
            st.session_state['parser'] = parser
            st.success(f"{parser_type} Parser built successfully!")
            if parser.conflicts:
                st.warning(f"Detected {len(parser.conflicts)} parsing table conflict(s). Open 'Conflicts Report' to inspect details.")

    if 'parser' in st.session_state:
        parser = st.session_state['parser']
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("States", len(parser.C))
        col2.metric("ACTION Entries", len(parser.action))
        col3.metric("GOTO Entries", len(parser.goto_table))
        col4.metric("Conflicts", len(parser.conflicts))

        st.markdown("<div class='section-title'>Parser Explorer</div>", unsafe_allow_html=True)
        feature = st.selectbox("Select a feature to display:", [
            "Augmented Grammar",
            "FIRST Sets",
            "FOLLOW Sets",
            "Canonical Collection of Items",
            "ACTION Table",
            "GOTO Table",
            "Conflicts Report",
            "Parse Input String",
        ])

        if feature == "Augmented Grammar":
            st.markdown("### Augmented Grammar")
            for idx, prod in enumerate(parser.grammar.productions):
                st.write(f"{idx}: {prod[0]} -> {' '.join(prod[1])}")
        elif feature == "FIRST Sets":
            if parser.grammar.first is None:
                parser.grammar.compute_first()
            st.markdown("### FIRST Sets")
            for symbol, first_set in parser.grammar.first.items():
                st.write(f"FIRST({symbol}) = {{ {', '.join(first_set)} }}")
        elif feature == "FOLLOW Sets":
            if parser.grammar.follow is None:
                parser.grammar.compute_follow()
            st.markdown("### FOLLOW Sets")
            for symbol, follow_set in parser.grammar.follow.items():
                st.write(f"FOLLOW({symbol}) = {{ {', '.join(follow_set)} }}")
        elif feature == "Canonical Collection of Items":
            st.markdown("### Canonical Collection of Items")
            for idx, I in enumerate(parser.C):
                st.write(f"**I{idx}:**")
                for item in I:
                    st.write(f"  {item}")
            canonical_table = _build_canonical_collection_table(parser.C)
            st.download_button("Download canonical collection as CSV", data=canonical_table.to_csv(index=False).encode("utf-8"), file_name="canonical_collection.csv", mime="text/csv")
        elif feature == "ACTION Table":
            st.markdown("### ACTION Table")
            action_table = _build_transition_table(parser.action, "State")
            st.dataframe(action_table, use_container_width=True)
            st.download_button("Download ACTION table as CSV", data=action_table.to_csv().encode("utf-8"), file_name="action_table.csv", mime="text/csv")
        elif feature == "GOTO Table":
            st.markdown("### GOTO Table")
            goto_table = _build_transition_table(parser.goto_table, "State")
            st.dataframe(goto_table, use_container_width=True)
            st.download_button("Download GOTO table as CSV", data=goto_table.to_csv().encode("utf-8"), file_name="goto_table.csv", mime="text/csv")
        elif feature == "Conflicts Report":
            st.markdown("### Conflicts Report")
            if parser.conflicts:
                conflicts_table = _build_conflicts_table(parser.conflicts)
                st.dataframe(conflicts_table, use_container_width=True)
                st.download_button("Download conflicts report as CSV", data=conflicts_table.to_csv(index=False).encode("utf-8"), file_name="parser_conflicts.csv", mime="text/csv")
            else:
                st.success("No parser conflicts detected for this grammar and parser type.")
        elif feature == "Parse Input String":
            st.markdown("### Parse Input String")
            input_string = st.text_input("Enter the input string (tokens separated by spaces):")
            if st.button("Parse Input"):
                tokens = input_string.split()
                try:
                    configurations = parser.parse(tokens)
                    if configurations is None or configurations[-1][2] != ('accept',):
                        st.error("Parsing failed.")
                        return
                    st.success("Input string parsed successfully!")
                    st.write("**Parsing Steps:**")
                    steps_data = []
                    for step in configurations:
                        steps_data.append({
                            "Stack": ' '.join(map(str, step[0])),
                            "Remaining Input": ' '.join(step[1]),
                            "Action": str(step[2]),
                        })
                    st.dataframe(pd.DataFrame(steps_data), use_container_width=True)
                except ValueError as e:
                    st.error(f"Error during parsing: {e}")
