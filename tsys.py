import graph


class GraphTS(graph.Graph):
    def __init__(self):
        super(GraphTS, self).__init__()

        # Additional class attributes
        self.map_state2node = dict()
        self.actions = None
        self.atoms = None
        self.deterministic = True
        self.qualitative = True
        self.turn_based = True

    def __repr__(self):
        return f"<GraphTS with |V|={self.number_of_nodes()}, |E|={self.number_of_edges()}>"

    def states(self):
        return self.nodes()

    def actions(self):
        return self.actions

    def enabled_actions(self, state):
        pass

    def delta(self, state, act):
        pass

    def node2state(self, node):
        pass

    def state2node(self, state):
        return self.map_state2node[state]

