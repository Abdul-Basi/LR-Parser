from src.items.lr0_item import LR0Item


class LR1Item(LR0Item):
    def __init__(self, lhs, rhs, dot_position=0, lookaheads=None):
        super().__init__(lhs, rhs, dot_position)
        self.lookaheads = set(lookaheads) if lookaheads else set()

    def __eq__(self, other):
        return super().__eq__(other) and self.lookaheads == other.lookaheads

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot_position, tuple(sorted(self.lookaheads))))

    def __repr__(self):
        rhs_with_dot = self.rhs[:]
        rhs_with_dot.insert(self.dot_position, '•')
        la = ','.join(self.lookaheads)
        return f"{self.lhs} -> {' '.join(rhs_with_dot)}, {{{la}}}"
