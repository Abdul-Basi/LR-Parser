import unittest

from src.ui.app import (
    _apply_grammar_preset,
    _get_grammar_presets,
    _infer_missing_symbols,
    _parse_productions,
    _split_symbols,
)


class TestAppHelpers(unittest.TestCase):
    def test_get_grammar_presets_returns_expected_keys(self):
        presets = _get_grammar_presets()

        self.assertIn("Arithmetic Expressions", presets)
        self.assertIn("Simple Assignment", presets)
        self.assertIn("If Else (Dangling Else)", presets)
        self.assertIn("productions", presets["Arithmetic Expressions"])

    def test_apply_grammar_preset_updates_session_state(self):
        presets = _get_grammar_presets()
        session_state = {
            "non_terminals_input": "",
            "terminals_input": "",
            "start_symbol_input": "",
            "productions_input": "",
        }

        applied = _apply_grammar_preset(session_state, "Arithmetic Expressions", presets)

        self.assertTrue(applied)
        self.assertEqual(session_state["start_symbol_input"], "E")
        self.assertIn("E2", session_state["non_terminals_input"])
        self.assertIn("E -> T E2", session_state["productions_input"])

    def test_apply_grammar_preset_custom_or_unknown(self):
        presets = _get_grammar_presets()
        session_state = {
            "non_terminals_input": "X",
            "terminals_input": "y",
            "start_symbol_input": "S",
            "productions_input": "S -> y",
        }

        custom_applied = _apply_grammar_preset(session_state, "Custom", presets)
        unknown_applied = _apply_grammar_preset(session_state, "Unknown", presets)

        self.assertFalse(custom_applied)
        self.assertFalse(unknown_applied)
        self.assertEqual(session_state["non_terminals_input"], "X")

    def test_split_symbols_handles_commas_and_spaces(self):
        self.assertEqual(_split_symbols("E, T, F"), ["E", "T", "F"])
        self.assertEqual(_split_symbols("id + * ( )"), ["id", "+", "*", "(", ")"])

    def test_parse_productions_collects_symbols(self):
        productions_text = """E -> T E2
E2 -> + T E2 | ε
T -> F T2
T2 -> * F T2 | ε
F -> ( E ) | id
"""

        productions_list, lhs_symbols, rhs_symbols = _parse_productions(productions_text)

        self.assertEqual(
            productions_list,
            [
                ("E", ["T", "E2"]),
                ("E2", ["+", "T", "E2"]),
                ("E2", ["ε"]),
                ("T", ["F", "T2"]),
                ("T2", ["*", "F", "T2"]),
                ("T2", ["ε"]),
                ("F", ["(", "E", ")"]),
                ("F", ["id"]),
            ],
        )
        self.assertEqual(lhs_symbols, {"E", "E2", "T", "T2", "F"})
        self.assertIn("id", rhs_symbols)
        self.assertIn("E2", rhs_symbols)
        self.assertIn("ε", rhs_symbols)

    def test_infer_missing_symbols_adds_undeclared_symbols(self):
        productions_list = [
            ("E", ["T", "E2"]),
            ("E2", ["+", "T", "E2"]),
            ("E2", ["ε"]),
            ("T", ["F", "T2"]),
            ("T2", ["*", "F", "T2"]),
            ("T2", ["ε"]),
            ("F", ["(", "E", ")"]),
            ("F", ["id"]),
        ]

        non_terminals, terminals, inferred_non_terminals, inferred_terminals = _infer_missing_symbols(
            ["E", "T", "F"],
            ["id", "+", "*", "(", ")"],
            productions_list,
        )

        self.assertEqual(non_terminals, ["E", "T", "F", "E2", "T2"])
        self.assertEqual(terminals, ["id", "+", "*", "(", ")"])
        self.assertEqual(inferred_non_terminals, ["E2", "T2"])
        self.assertEqual(inferred_terminals, [])


if __name__ == "__main__":
    unittest.main()
