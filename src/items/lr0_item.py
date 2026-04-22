class LR0Item:
    def __init__(self, lhs, rhs, dot_position=0):
        self.lhs = lhs
        self.rhs = rhs
        self.dot_position = dot_position

    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs and self.dot_position == other.dot_position

    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs), self.dot_position))

    def __repr__(self):
        rhs_with_dot = self.rhs[:]
        rhs_with_dot.insert(self.dot_position, '•')
        return f"{self.lhs} -> {' '.join(rhs_with_dot)}"
