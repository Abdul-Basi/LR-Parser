import unittest

from src.ui.app import _build_canonical_collection_table, _build_conflicts_table, _build_transition_table


class TestTableExports(unittest.TestCase):
    def test_build_transition_table_formats_state_index(self):
        mapping = {
            (0, 'id'): ('shift', 1),
            (0, '('): ('shift', 2),
            (1, '$'): ('accept',),
        }

        table = _build_transition_table(mapping, 'State')

        self.assertEqual(table.index.name, 'State')
        self.assertEqual(table.loc[0, 'id'], "('shift', 1)")
        self.assertEqual(table.loc[0, '('], "('shift', 2)")
        self.assertEqual(table.loc[1, '$'], "('accept',)")

    def test_build_canonical_collection_table_flattens_items(self):
        collection = [
            {"S' -> • S", "S -> • A b"},
            {"S -> A • b"},
        ]

        table = _build_canonical_collection_table(collection)

        self.assertEqual(list(table.columns), ["State", "Item"])
        self.assertEqual(set(table["State"]), {"I0", "I1"})
        self.assertEqual(
            set(table[table["State"] == "I0"]["Item"]),
            {"S' -> • S", "S -> • A b"},
        )
        self.assertEqual(
            set(table[table["State"] == "I1"]["Item"]),
            {"S -> A • b"},
        )

    def test_build_conflicts_table_formats_rows(self):
        conflicts = [
            {
                'state': 4,
                'symbol': '+',
                'conflict_type': 'shift-reduce',
                'existing_action': ('shift', 7),
                'incoming_action': ('reduce', 'E', ['T']),
            }
        ]

        table = _build_conflicts_table(conflicts)

        self.assertEqual(
            list(table.columns),
            [
                "State",
                "Symbol",
                "Conflict Type",
                "Existing Action",
                "Incoming Action",
                "Explanation",
                "Suggested Refactor",
            ],
        )
        self.assertEqual(table.loc[0, 'State'], 4)
        self.assertEqual(table.loc[0, 'Symbol'], '+')
        self.assertEqual(table.loc[0, 'Conflict Type'], 'shift-reduce')
        self.assertEqual(table.loc[0, 'Existing Action'], "('shift', 7)")
        self.assertEqual(table.loc[0, 'Incoming Action'], "('reduce', 'E', ['T'])")
        self.assertIn("competing actions", table.loc[0, 'Explanation'])
        self.assertIn("precedence", table.loc[0, 'Suggested Refactor'])

    def test_build_conflicts_table_dangling_else_hint(self):
        conflicts = [
            {
                'state': 12,
                'symbol': 'else',
                'conflict_type': 'shift-reduce',
                'existing_action': ('shift', 20),
                'incoming_action': ('reduce', 'L', ['ε']),
            }
        ]

        table = _build_conflicts_table(conflicts)

        self.assertIn("dangling-else", table.loc[0, 'Suggested Refactor'])


if __name__ == '__main__':
    unittest.main()
