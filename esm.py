from abc import ABC, abstractmethod


class ESM(ABC):
    def __init__(self, graph, len_history=float("inf")):
        self.graph = graph
        self.state_history = []
        self.action_history = []
        self.step_counter = None
        self.len_history = len_history

    def initialize(self, state):
        self.state_history = []
        self.action_history = []
        self.state_history.append(state)
        self.step_counter = 0
        node = self.graph.state2node(state)
        print(f"[INFO] Initialized ESM to node:: {node}:{state}")

    @property
    def curr_state(self):
        if self.step_counter is None:
            raise ValueError("ESM is not initialized. Current state is undefined.")
        return self.state_history[self.step_counter]

    @abstractmethod
    def step_forward(self):
        pass

    @abstractmethod
    def step_backward(self):
        pass
