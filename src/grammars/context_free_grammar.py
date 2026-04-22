from src.grammars.grammar import Grammar


class ContextFreeGrammar(Grammar):
    """Context-free grammar with FIRST/FOLLOW computation."""

    def __init__(self, terminals, non_terminals, productions, start_symbol):
        super().__init__(terminals, non_terminals, productions, start_symbol)
        self.first = None
        self.follow = None

    def compute_first(self):
        self.first = {symbol: set() for symbol in self.non_terminals + self.terminals}
        for terminal in self.terminals:
            self.first[terminal].add(terminal)

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.productions:
                before = self.first[lhs].copy()
                if rhs == ['ε']:
                    self.first[lhs].add('ε')
                else:
                    count = 0
                    for symbol in rhs:
                        if symbol in self.first:
                            self.first[lhs].update(self.first[symbol] - {'ε'})
                        if symbol not in self.first or 'ε' not in self.first[symbol]:
                            break
                        count += 1
                    if count == len(rhs):
                        self.first[lhs].add('ε')
                if before != self.first[lhs]:
                    changed = True

    def compute_follow(self):
        self.follow = {symbol: set() for symbol in self.non_terminals}
        if self.start_symbol in self.follow:
            self.follow[self.start_symbol].add('$')

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.productions:
                if lhs not in self.follow:
                    self.follow[lhs] = set()
                trailer = self.follow[lhs].copy()
                for symbol in reversed(rhs):
                    if symbol in self.non_terminals:
                        if symbol not in self.follow:
                            self.follow[symbol] = set()
                        before = self.follow[symbol].copy()
                        self.follow[symbol].update(trailer)
                        if symbol in self.first and 'ε' in self.first[symbol]:
                            trailer.update(self.first[symbol] - {'ε'})
                        elif symbol in self.first:
                            trailer = self.first[symbol].copy()
                        if before != self.follow[symbol]:
                            changed = True
                    elif symbol in self.terminals:
                        trailer = self.first[symbol].copy() if symbol in self.first else {symbol}
