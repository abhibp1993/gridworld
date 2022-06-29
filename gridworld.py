import graph
from abc import ABC, abstractmethod
from gw_utils import GW_OBS_TYPE_SINK, GW_BOUNDARY_TYPE_BOUNCY


RESERVED_PROPERTIES = {"turn", "state", "action", "prob", "label"}


class Gridworld(ABC):
    def __init__(self, dim, deterministic=True, qualitative=True, turn_based=True,
                 obs_type=GW_OBS_TYPE_SINK, boundary_type=GW_BOUNDARY_TYPE_BOUNCY):
        """
        (state/trans)_properties is a mapping from p-name to PropertyMap.
        """
        self.dim = dim
        self.qualitative = qualitative
        self.deterministic = deterministic
        self.turn_based = turn_based
        self.obs_type = obs_type
        self.boundary_type = boundary_type

    def __repr__(self):
        if self.deterministic:
            return f"<Deterministic Gridworld with dim={self.dim}>"
        else:
            if self.qualitative:
                return f"<Stochastic Gridworld (Qualitative) with dim={self.dim}>"
            return f"<Stochastic Gridworld (Quantitative) with dim={self.dim}>"

    @abstractmethod
    def states(self):
        pass

    @abstractmethod
    def actions(self):
        pass

    @abstractmethod
    def delta(self, state, act):
        pass

    def atoms(self):
        raise NotImplementedError("atoms function is not implemented by the user.")

    def label(self, state):
        raise NotImplementedError("label function is not implemented by the user.")


class Graph(graph.Graph):
    def __init__(self):
        super(Graph, self).__init__()

        # Additional class attributes
        self.map_state2node = dict()
        self.actions = None
        self.atoms = None
        self.deterministic = True
        self.qualitative = True
        self.turn_based = True


def graphify(obj: Gridworld, state_properties=None, trans_properties=None):
    if state_properties is None:
        state_properties = dict()

    if trans_properties is None:
        trans_properties = dict()

    # Clear graph.
    graph = Graph()
    graph.map_state2node = dict()

    # Update options
    graph.turn_based = obj.turn_based
    graph.deterministic = obj.deterministic
    graph.qualitative = obj.qualitative
    graph.actions = obj.actions()
    graph.atoms = obj.atoms()

    # Define state properties.
    _update_state_properties(graph, state_properties)

    # Define transition_properties.
    _update_transition_properties(graph, trans_properties)

    # Add states.
    _update_states(graph, obj)

    # Add transitions.
    _update_transitions(graph, obj)

    # Generate labels for all states if user has implemented atoms, label functions.
    _make_labeled(graph, obj)

    return graph


def _update_state_properties(graph, state_properties):
    # Ensure no reserved property names are used
    common_props = set(state_properties.keys()).intersection(RESERVED_PROPERTIES)
    if len(common_props) > 0:
        raise NameError(f"Cannot use reserved property names {common_props} as state_properties.")

    # Add properties based on transition system properties
    state_properties |= {"state": None}

    if graph.turn_based:
        state_properties |= {"turn": -1}

    try:
        if len(graph.atoms) > 0:
            state_properties |= {"label": set()}
    except NotImplementedError:
        pass

    # Add state properties
    for name, default in state_properties.items():
        graph.add_node_property(name, default)


def _update_transition_properties(graph, trans_properties):
    # Ensure no reserved property names are used
    common_props = set(trans_properties.keys()).intersection(RESERVED_PROPERTIES)
    if len(common_props) > 0:
        raise NameError(f"Cannot use reserved property names {common_props} as transition_properties.")

    # Add transition properties
    trans_properties |= {"action": None}

    if not graph.deterministic and not graph.qualitative:
        trans_properties |= {"prob": -1}

    # Add transition properties
    for name, default in trans_properties.items():
        graph.add_edge_property(name, default)


def _update_states(graph, obj):
    states = obj.states()

    # Add nodes to graph
    graph.add_nodes(num_nodes=len(states))

    # Update node to state mapping
    nid = 0
    for state in states:
        graph.set_node_property("state", nid, state)
        graph.map_state2node[state] = nid
        nid += 1


def _update_transitions(graph, obj):
    if obj.deterministic:
        _update_transitions_deterministic(graph, obj)
    else:
        if obj.qualitative:
            _update_transitions_qualitative(graph, obj)
        else:
            _update_transitions_quantitative(graph, obj)


def _make_labeled(graph, obj):
    try:
        for nid in graph.nodes():
            state = graph.get_node_property("state", nid)
            graph.set_node_property("label", nid, obj.label(state))
    except NotImplementedError:
        graph.atoms = None


def _update_transitions_deterministic(graph, obj):
    for state in obj.states():
        for act in obj.actions():
            n_state = obj.delta(state, act)
            assert n_state in obj.states(), f"{n_state} is not in transition system."

            # Get nodes corresponding to states
            u = graph.map_state2node[state]
            v = graph.map_state2node[n_state]
            graph.add_edge(u, v, action=act)


def _update_transitions_qualitative(graph, obj):
    for state in obj.states():
        for act in obj.actions():
            n_states = list(obj.delta(state, act))
            assert all(st in obj.states() for st in n_states), \
                f"Not all states in {n_states} are in transition system."
            graph.add_edges_from([
                (graph.map_state2node[state], graph.map_state2node[n_state], {"action": act}) for n_state in n_states]
            )


def _update_transitions_quantitative(graph, obj):
    for state in obj.states():
        for act in obj.actions():
            n_states = list(obj.delta(state, act))
            assert all(st in obj.states() for st, _ in n_states), \
                f"Not all states in {n_states} are in transition system."
            assert sum(p for _, p in n_states) == 1.0, \
                f"Probabilities in {n_states} do not sum to 1.0."
            graph.add_edges_from([
                (graph.map_state2node[state], graph.map_state2node[n_state], {"action": act, "prob": p})
                for n_state, p in n_states
            ])