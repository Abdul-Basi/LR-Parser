from src.parsers.lr0_parser import LR0Parser


class SLR1Parser(LR0Parser):
    def __init__(self, context_free_grammar):
        super().__init__(context_free_grammar)
        self.grammar.compute_follow()

    def construct_parsing_table(self):
        for I in self.C:
            state_no = self.states[frozenset(I)]
            for item in I:
                if item.dot_position < len(item.rhs):
                    symbol = item.rhs[item.dot_position]
                    if symbol in self.grammar.terminals:
                        next_state = self.transitions.get((state_no, symbol))
                        if next_state is not None:
                            self._set_action(state_no, symbol, ('shift', next_state))
                else:
                    if item.lhs == self.grammar.augmented_start_symbol:
                        self._set_action(state_no, '$', ('accept',))
                    else:
                        for follow_symbol in self.grammar.follow[item.lhs]:
                            self._set_action(state_no, follow_symbol, ('reduce', item.lhs, item.rhs))
            for A in self.grammar.non_terminals:
                next_state = self.transitions.get((state_no, A))
                if next_state is not None:
                    self.goto_table[(state_no, A)] = next_state
