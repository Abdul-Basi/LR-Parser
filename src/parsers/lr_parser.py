from abc import ABC, abstractmethod


class LRParser(ABC):
    def __init__(self, context_free_grammar):
        self.grammar = context_free_grammar
        self.grammar.augment_grammar()
        self.grammar.compute_first()
        self.action = {}
        self.goto_table = {}
        self.states = {}
        self.transitions = {}
        self.C = []
        self.conflicts = []

    def _set_action(self, state, symbol, action_value):
        action_key = (state, symbol)
        existing_action = self.action.get(action_key)
        if existing_action is None:
            self.action[action_key] = action_value
        elif existing_action != action_value:
            self.conflicts.append({
                'state': state,
                'symbol': symbol,
                'existing_action': existing_action,
                'incoming_action': action_value,
                'conflict_type': f"{existing_action[0]}-{action_value[0]}",
            })

    @abstractmethod
    def items(self):
        pass

    @abstractmethod
    def construct_parsing_table(self):
        pass

    def parse(self, input_string):
        input_string = input_string + ['$']
        stack = [0]
        index = 0
        configurations = []
        while True:
            state = stack[-1]
            token = input_string[index]
            action = self.action.get((state, token))
            configurations.append((stack[:], input_string[index:], action))
            if action is None:
                print(f"Error: no action defined for state {state} and token '{token}'")
                return
            if action[0] == 'shift':
                stack.append(action[1])
                index += 1
            elif action[0] == 'reduce':
                lhs = action[1]
                rhs = action[2]
                for _ in rhs:
                    stack.pop()
                state = stack[-1]
                goto_state = self.goto_table.get((state, lhs))
                if goto_state is None:
                    print(f"Error: no goto state for state {state} and non-terminal '{lhs}'")
                    return
                stack.append(goto_state)
            elif action[0] == 'accept':
                break
            else:
                print(f"Error: unknown action {action}")
                return
        return configurations
