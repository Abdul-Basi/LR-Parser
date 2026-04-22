from collections import deque

from src.items.lr0_item import LR0Item
from src.parsers.lr_parser import LRParser


class LR0Parser(LRParser):
    def items(self):
        initial_item = LR0Item(self.grammar.augmented_start_symbol, [self.grammar.start_symbol], 0)
        I0 = self.closure({initial_item})
        self.C.append(I0)
        self.states[frozenset(I0)] = 0
        queue = deque([I0])
        while queue:
            I = queue.popleft()
            state_no = self.states[frozenset(I)]
            symbols = set()
            for item in I:
                if item.dot_position < len(item.rhs):
                    symbols.add(item.rhs[item.dot_position])
            for X in symbols:
                goto_I_X = self.goto(I, X)
                if goto_I_X:
                    goto_I_X_frozenset = frozenset(goto_I_X)
                    if goto_I_X_frozenset not in self.states:
                        self.states[goto_I_X_frozenset] = len(self.C)
                        self.C.append(goto_I_X)
                        queue.append(goto_I_X)
                    self.transitions[(state_no, X)] = self.states[goto_I_X_frozenset]

    def closure(self, items):
        closure_set = set(items)
        added = True
        while added:
            added = False
            new_items = set()
            for item in closure_set:
                if item.dot_position < len(item.rhs):
                    symbol = item.rhs[item.dot_position]
                    if symbol in self.grammar.non_terminals:
                        for prod in self.grammar.productions:
                            if prod[0] == symbol:
                                new_item = LR0Item(prod[0], prod[1], 0)
                                if new_item not in closure_set:
                                    new_items.add(new_item)
                                    added = True
            closure_set.update(new_items)
        return closure_set

    def goto(self, items, symbol):
        goto_set = set()
        for item in items:
            if item.dot_position < len(item.rhs) and item.rhs[item.dot_position] == symbol:
                goto_set.add(LR0Item(item.lhs, item.rhs, item.dot_position + 1))
        return self.closure(goto_set)

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
                        for term_symbol in self.grammar.terminals + ['$']:
                            self._set_action(state_no, term_symbol, ('reduce', item.lhs, item.rhs))
            for A in self.grammar.non_terminals:
                next_state = self.transitions.get((state_no, A))
                if next_state is not None:
                    self.goto_table[(state_no, A)] = next_state
