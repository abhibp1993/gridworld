import logging
from graph import Graph


class Gridworld(Graph):
    RESERVED_PROPERTIES = {"turn", "state", "action", "prob", "label"}

    def __init__(self, tsgen, graphify=True):
        super(Gridworld, self).__init__()

        # Gridworld properties
        self.dim = None
        self.obs = None
        self.obs_type = None

        # Transition system representation
        self.states = None
        self.actions = None
        self.delta = None
        self.atoms = None
        self.label = None

        # Generator object, options
        self.tsgen = tsgen
        self.graphify = graphify
        self.qualitative = None
        self.deterministic = None
        self.turn_based = None

        # Inverse state to node map
        self.map_state2node = dict()

        # Construct gridworld
        self._construct_gridworld()

    def __str__(self):
        if self.deterministic:
            return f"<Gridworld (Det.) with dim={self.dim}, graphify={self.graphify}>"
        else:
            if self.qualitative:
                return f"<Gridworld (Qual. Stoch.) with dim={self.dim}, graphify={self.graphify}>"
            return f"<Gridworld (Quant. Stoch.) with dim={self.dim}, graphify={self.graphify}>"

    def __repr__(self):
        return f"<Gridworld with dim={self.dim}, det={self.deterministic}, tb={self.turn_based}, " \
               f"qual={self.qualitative}, graphify={self.graphify}>"

    def __getstate__(self):
        if self.graphify is False:
            raise TypeError("Gridworld must be graphified before saving.")

        attr_to_serialize = [
            "dim",
            "obs",
            "obs_type",
            "qualitative",
            "deterministic",
            "turn_based",
            "map_state2node",
            "states",
            "actions",
            "atoms",
            "graphify"
        ]

        graph_dict = super(Gridworld, self).__getstate__()
        gw_dict = {k: self.__dict__[k] for k in attr_to_serialize}
        return graph_dict | gw_dict

    def __setstate__(self, obj_dict):
        self.__dict__ |= obj_dict
        self.delta = self._delta
        if "label" in obj_dict["_v_props"]:
            self.label = self._label

    def _construct_gridworld(self):
        # Load gridworld properties
        self._update_gw_properties()

        # Construct gridworld in explicit or symbolic representation
        if self.graphify:
            self._construct_graph()
        else:
            # Bind gridworld methods to user provided TSGenerator methods.
            #   Note. If defined, state2node, node2state methods will be ignored since
            #   they are used to map between node and states when the game is graphified.
            self.states = self.tsgen.states
            self.actions = self.tsgen.actions
            self.delta = self.tsgen.delta
            self.atoms = self.tsgen.atoms
            self.label = self.tsgen.label

    def _construct_graph(self):
        # Clear graph.
        self.clear()

        # Define state properties.
        self._update_state_properties()

        # Define transition_properties.
        self._update_transition_properties()

        # Add states.
        self._update_states()

        # Add actions.
        self._update_actions()

        # Add transitions.
        self._update_transitions()

        # Generate labels for all states if user has implemented atoms, label functions.
        self._make_labeled()

    def save(self, file):
        raise NotImplementedError("Not yet implemented")

    @classmethod
    def load(cls, file):
        raise NotImplementedError("Not yet implemented.")

    def _delta(self, state, act):
        # Get node corresponding to state
        uid = self.map_state2node[state]

        # Get all out edges from that state
        out_edges = self.out_edges(uid)

        # Get next states
        next_states = []
        for u, v, k in out_edges:
            edge_act = self.get_edge_property("action", (u, v, k))
            if edge_act == act:
                # If TS is quantitative, associate probability values.
                if not self.deterministic and not self.qualitative:
                    prob = self.get_edge_property("prob", (u, v, k))
                    next_states.append((self.get_node_property("state", v), prob))
                else:
                    next_states.append(self.get_node_property("state", v))

        # Return next states based on whether TS is deterministic or not.
        if self.deterministic:
            return next_states[0]
        else:
            return next_states

    def _label(self, state):
        # Get node corresponding to state
        uid = self.map_state2node[state]

        return self.get_node_property("label", uid)

    def _update_gw_properties(self):
        """
        Load gridworld properties.

        :raises: The following errors are possible:
            * AttributeError (for tsgen.dim()): dim() function is not defined in TSGenerator class.
            * TypeError (for tsgen.dim()): dim is defined TSGenerator class but is not callable.
            * TypeError (for tsgen.obs()): obs is defined TSGenerator class but is not callable.
        """
        self.dim = self.tsgen.dim()
        if hasattr(self.tsgen, "obj"):
            self.obs = self.tsgen.obs()
        self.turn_based = self.tsgen.TURN_BASED
        self.qualitative = self.tsgen.QUALITATIVE
        self.deterministic = self.tsgen.DETERMINISTIC
        logging.info(f"Loaded gridworld with properties:"
                     f"\n* dim: {self.dim},"
                     f"\n* obs: {self.obs},"
                     f"\n* turn_based: {self.turn_based},"
                     f"\n* qualitative: {self.qualitative},"
                     f"\n* deterministic: {self.deterministic}"
                     )

    def _update_state_properties(self):
        # Get user defined state (node) properties.
        user_props = self.tsgen.state_properties()

        # Ensure no reserved property names are used
        common_props = set(user_props.keys()).intersection(self.RESERVED_PROPERTIES)
        if len(common_props) > 0:
            raise NameError(f"Cannot use reserved property names {common_props} as state_properties.")

        # Add properties based on transition system properties
        user_props |= {"state": None}

        if self.turn_based:
            user_props |= {"turn": -1}

        try:
            if len(self.tsgen.atoms()) > 0:
                user_props |= {"label": -1}
        except NotImplementedError:
            pass

        # Add state properties
        for name, default in user_props.items():
            self.add_node_property(name, default)

    def _update_transition_properties(self):
        # Get user defined state (node) properties.
        user_props = self.tsgen.transition_properties()

        # Ensure no reserved property names are used
        common_props = set(user_props.keys()).intersection(self.RESERVED_PROPERTIES)
        if len(common_props) > 0:
            raise NameError(f"Cannot use reserved property names {common_props} as transition_properties.")

        # Add transition properties
        user_props |= {"action": None}

        if not self.deterministic and not self.qualitative:
            user_props |= {"prob": -1}

        # Add transition properties
        for name, default in user_props.items():
            self.add_edge_property(name, default)

        self.delta = self._delta

    def _update_states(self):
        # Add nodes to graph
        self.add_nodes(num_nodes=len(self.tsgen.states()))

        # Update node to state mapping
        nid = 0
        for state in self.tsgen.states():
            self.set_node_property("state", nid, state)
            self.map_state2node[state] = nid
            nid += 1

        self.states = set(self.tsgen.states())

    def _update_actions(self):
        self.actions = set(self.tsgen.actions())

    def _update_transitions(self):
        if self.deterministic:
            self._update_transitions_deterministic()
        else:
            if self.qualitative:
                self._update_transitions_qualitative()
            else:
                self._update_transitions_quantitative()
            
    def _make_labeled(self):
        try:
            self.atoms = self.tsgen.atoms()
            for nid in self.nodes():
                state = self.get_node_property("state", nid)
                self.set_node_property("label", nid, self.tsgen.label(state))
            self.label = self._label
        except NotImplementedError:
            self.atoms = None
            self.label = None

    def _update_transitions_deterministic(self):
        for state in self.states:
            for act in self.actions:
                n_state = self.tsgen.delta(state, act)
                assert n_state in self.states, f"{n_state} is not in transition system."

                # Get nodes corresponding to states
                u = self.map_state2node[state]
                v = self.map_state2node[n_state]
                self.add_edge(u, v, action=act)

    def _update_transitions_qualitative(self):
        for state in self.states:
            for act in self.actions:
                n_states = list(self.tsgen.delta(state, act))
                assert all(st in self.states for st in n_states), \
                    f"Not all states in {n_states} are in transition system."
                self.add_edges_from([
                    (self.map_state2node[state], self.map_state2node[n_state], {"action": act}) for n_state in n_states]
                )

    def _update_transitions_quantitative(self):
        for state in self.states:
            for act in self.actions:
                n_states = list(self.tsgen.delta(state, act))
                assert all(st in self.states for st, _ in n_states), \
                    f"Not all states in {n_states} are in transition system."
                assert sum(p for _, p in n_states) == 1.0, \
                    f"Probabilities in {n_states} do not sum to 1.0."
                self.add_edges_from([
                    (self.map_state2node[state], self.map_state2node[n_state], {"action": act, "prob": p})
                    for n_state, p in n_states
                ])
