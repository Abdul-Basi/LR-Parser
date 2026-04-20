from collections import defaultdict

from src.items.lr0_item import LR0Item
from src.items.lr1_item import LR1Item
from src.parsers.lr1_parser import LR1Parser


class LALR1Parser(LR1Parser):
    def merge_states(self):
        state_groups = defaultdict(list)
        for idx, I in enumerate(self.C):
            core = frozenset([LR0Item(item.lhs, item.rhs, item.dot_position) for item in I])
            state_groups[core].append((idx, I))

        new_states = {}
        new_C = []
        state_mapping = {}
        for core, states in state_groups.items():
            merged_items_dict = {}
            for idx, items in states:
                for item in items:
                    key = (item.lhs, tuple(item.rhs), item.dot_position)
                    merged_items_dict.setdefault(key, set()).update(item.lookaheads)
            new_items = set()
            for key, lookaheads in merged_items_dict.items():
                new_items.add(LR1Item(key[0], list(key[1]), key[2], lookaheads))
            state_no = len(new_C)
            for idx, _ in states:
                state_mapping[idx] = state_no
            new_states[frozenset(new_items)] = state_no
            new_C.append(new_items)

        new_transitions = {}
        for (old_state, symbol), new_state in self.transitions.items():
            from_state = state_mapping[old_state]
            to_state = state_mapping[new_state]
            new_transitions[(from_state, symbol)] = to_state

        self.states = {frozenset(I): idx for idx, I in enumerate(new_C)}
        self.transitions = new_transitions
        self.C = new_C

    def construct_parsing_table(self):
        self.merge_states()
        super().construct_parsing_table()
