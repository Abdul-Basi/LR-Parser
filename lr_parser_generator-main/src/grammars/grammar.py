class Grammar:
    """Represents a general grammar with terminals, non-terminals, productions, and a start symbol."""

    def __init__(self, terminals, non_terminals, productions, start_symbol):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions
        self.start_symbol = start_symbol
        self.augmented_start_symbol = None
        self.production_numbers = None

    def augment_grammar(self):
        self.augmented_start_symbol = self.start_symbol + "'"
        self.productions.insert(0, (self.augmented_start_symbol, [self.start_symbol]))
        self.non_terminals.insert(0, self.augmented_start_symbol)
        self.number_productions()

    def number_productions(self):
        self.production_numbers = {}
        for idx, prod in enumerate(self.productions):
            self.production_numbers[(prod[0], tuple(prod[1]))] = idx

    def get_production_number(self, prod):
        return self.production_numbers.get((prod[0], tuple(prod[1])))
