import pickle
import os.path
import networkx as nx


class Graph:
    """
    Graph representation:
        1. nodes: stores the maximum index of node in graph.
        2. edges: stores a dictionary of out-edges in format {u: {v: k}}
        3. inv_edges: stores a dictionary of in-edges in format {v: set(u)}
        4. v_props: dictionary of node properties to NodePropertyMap() object.
        5. e_props: dictionary of edge properties to EdgePropertyMap() object.
        6. any user defined graph properties.
    """
    def __init__(self, *args, **kwargs):
        self._nodes = -1
        self._num_edges = -1
        self._edges = dict()
        self._inv_edges = dict()
        self._v_props = dict()
        self._e_props = dict()

    def __repr__(self):
        return f"<Graph with |V|={self.number_of_nodes()}, |E|={self.number_of_edges()}>"

    def __len__(self):
        return self.size()

    def __getstate__(self):
        serialized_graph = {
            "type": "multidigraph",
            "_nodes": self._nodes,
            "_num_edges": self._num_edges,
            "_edges": self._edges,
            "_inv_edges": self._inv_edges,
            "_v_props": self._v_props,
            "_e_props": self._e_props,
        }
        return serialized_graph

    def add_node(self, **kwargs):
        # Add node
        self._nodes += 1

        # Update properties
        for p_name in kwargs:
            if p_name in self._v_props:
                self._v_props[p_name][self._nodes] = kwargs[p_name]

        return self._nodes

    def add_nodes(self, num_nodes):
        """
        :param num_nodes: (int) number of nodes. Must be (strictly) greater than 0.
        """
        assert num_nodes >= 1, f"Expected num_nodes > 0. Received {num_nodes}."
        self._nodes += num_nodes
        return range(self._nodes - num_nodes + 1, self._nodes + 1)

    def add_nodes_from(self, list_of_props):
        """
        Adds multiple nodes to graph.
        :param list_of_props: (list of dict) Each dict is {property-name: property-value}.
        :return:
        """
        assert len(list_of_props) >= 1, f"Expected len(list_of_props) > 0. Received {len(list_of_props)}."

        # Add node
        self._nodes += len(list_of_props)

        # Update properties
        num_nodes = len(list_of_props)
        if len(list_of_props) != 0:
            for i in range(self._nodes - num_nodes + 1, self._nodes + 1):
                for p_name in list_of_props[i]:
                    self._v_props[p_name][i] = list_of_props[i][p_name]

        return range(self._nodes - num_nodes + 1, self._nodes + 1)

    def add_edge(self, u, v, **kwargs):
        assert u <= self._nodes and v <= self._nodes, f"u or v is not in graph."

        # Add edge
        #   (data structure: edges)
        if u not in self._edges:
            self._edges[u] = {v: 0}
        elif v not in self._edges[u]:
            self._edges[u][v] = 0
        else:
            self._edges[u][v] += 1

        #   (data structure: inv_edges)
        if v not in self._inv_edges:
            self._inv_edges[v] = {u}
        else:
            self._inv_edges[v].add(u)

        # Update properties
        k = self._edges[u][v]
        for p_name in kwargs:
            if p_name in self._e_props:
                self._e_props[p_name][(u, v, k)] = kwargs[p_name]

        # Update edge count
        self._num_edges += 1

        return u, v, k

    def add_edges_from(self, list_of_edges):
        """
        Adds multiple edges to graph.
        :param list_of_edges: (iterable of (u, v) or (u, v, kwargs)) type.
        :return:
        """
        edges = []
        for edge in list_of_edges:
            if len(edge) == 2:
                u, v = edge
                edges.append(self.add_edge(u, v))
            else:
                u, v, e_props = edge
                edges.append(self.add_edge(u, v, **e_props))

        return edges

    def rem_node(self, node):
        raise NotImplementedError("Node removal operation is not allowed. Use GraphView to filter nodes.")

    def rem_edge(self, u, v, k):
        """
        Removes edge (u, v, k) from graph.
        If `k = None`, then all edges between (u, v) are removed.

        :param u:
        :param v:
        :param k:
        :return:
        """
        raise NotImplementedError("rem_edge operation is not allowed. Use GraphView to filter edges.")

    def has_node(self, node):
        return node <= self._nodes

    def has_edge(self, edge):
        """
        Expects an edge of type (u, v) or (u, v, k).
        In former case, check if there exists an edge between u, v.
        In latter case, check if an edge with given `k` exists.
        :param edge:
        :return:
        """
        assert len(edge) in [2, 3], "Invalid edge. Edge must be in (u, v) or (u, v, k) format."
        try:
            if len(edge) == 2:
                return edge[0] in self._edges and \
                       edge[1] in self._edges[edge[0]]
            else:   # len(edge) == 3:
                return edge[0] in self._edges and \
                       edge[1] in self._edges[edge[0]] and \
                       edge[2] <= self._edges[edge[0]][edge[1]]
        except KeyError:
            pass

        return False

    def nodes(self):
        return range(self._nodes + 1)

    def edges(self, u=None, v=None):
        for u in self._edges:
            for v in self._edges[u]:
                for k in range(self._edges[u][v] + 1):
                    yield u, v, k

    def successors(self, node):
        if node not in self._edges:
            return

        for v in self._edges[node]:
            yield v

    def predecessors(self, node):
        if node not in self._inv_edges:
            return

        for u in self._inv_edges[node]:
            yield u

    def neighbors(self, node):
        for v in self.successors(node):
            yield v

        for u in self.predecessors(node):
            yield u

    def descendants(self, node):
        if node not in self._edges:
            return

        # Initialize queue
        queue = [u for u in self.successors(node)]
        visited = set()
        while len(queue) > 0:
            u = queue.pop()
            yield u
            visited.add(u)
            succ_u = set(self.successors(u)) - visited
            for v in succ_u:
                queue.append(v)

    def ancestors(self, node):
        if node not in self._inv_edges:
            return

        # Initialize queue
        queue = [v for v in self.predecessors(node)]
        visited = set()
        while len(queue) > 0:
            v = queue.pop()
            yield v
            visited.add(v)
            pred_v = set(self.predecessors(v)) - visited
            for u in pred_v:
                queue.append(u)

    def in_edges(self, node):
        for u in self.predecessors(node):
            for k in range(self._edges[u][node] + 1):
                yield u, node, k

    def out_edges(self, node):
        for v in self.successors(node):
            for k in range(self._edges[node][v] + 1):
                yield node, v, k

    def number_of_nodes(self):
        return self._nodes + 1

    def number_of_edges(self):
        return self._num_edges
        # return sum((self._edges[u][v] + 1 for u in self._edges for v in self._edges[u]))

    def size(self):
        return self.number_of_nodes() + self.number_of_edges()

    def clear(self):
        self._nodes = -1
        self._edges = dict()
        self._inv_edges = dict()
        self._v_props = dict()
        self._e_props = dict()

    def add_node_property(self, name, default=None):
        if name not in self._v_props:
            self._v_props[name] = NodePropertyMap(graph=self, default=default)
        # else:
            # logging.debug(f"add_node_property({name}) made no changes.")

    def has_node_property(self, name):
        return name in self._v_props

    def get_node_property(self, name, node):
        if self.has_node_property(name) and self.has_node(node):
            return self._v_props[name][node]
        raise ValueError(f"Either {name} is not valid node property or {node} is not in graph.")

    def set_node_property(self, name, node, value):
        if self.has_node_property(name) and self.has_node(node):
            self._v_props[name][node] = value
        else:
            raise ValueError(f"Either {name} is not valid node property or {node} is not in graph.")

    def add_edge_property(self, name, default=None):
        if name not in self._e_props:
            self._e_props[name] = EdgePropertyMap(graph=self, default=default)
        # else:
            # logging.debug(f"add_edge_property({name}) made no changes.")

    def has_edge_property(self, name):
        return name in self._e_props

    def get_edge_property(self, name, edge):
        if self.has_edge_property(name) and self.has_edge(edge):
            return self._e_props[name][edge]
        raise ValueError(f"Either {name} is not valid edge property or {edge} is not in graph.")

    def set_edge_property(self, name, edge, value):
        if self.has_edge_property(name) and self.has_edge(edge):
            self._e_props[name][edge] = value
        else:
            raise ValueError(f"Either {name} is not valid edge property or {edge} is not in graph.")

    def to_nx_graph(self):
        nx_graph = nx.MultiDiGraph()

        for node in range(self._nodes + 1):
            node_props = {p_name: self._v_props[p_name][node] for p_name in self._v_props}
            nx_graph.add_node(node, **node_props)

        for u, v, k in self.edges():
            edge_props = {p_name: self._e_props[p_name][(u, v, k)] for p_name in self._e_props}
            nx_graph.add_edge(u, v, key=k, **edge_props)

        return nx_graph

    def to_numpy(self):
        raise NotImplementedError("to_nx_graph")

    def to_esr_graph(self):
        return self

    def to_gen_graph(self):
        raise NotImplementedError("to_nx_graph")

    def to_bdd_graph(self):
        raise NotImplementedError("to_nx_graph")

    def save(self, file):
        ext = os.path.splitext(file)[1]
        if ext == ".graphml":
            raise NotImplementedError("save-load functionality for graphml is not ready.")
            # self._save_graphml(file)
        elif ext == ".graph":
            self._save_pickle(file)
        else:
            raise ValueError(f"Given file has extension: {ext}. Supported extensions: ['.graph']")

    # FIXME: make static, return graph.
    def load(self, file):
        self.clear()
        ext = os.path.splitext(file)[1]
        if ext == ".graphml":
            # raise NotImplementedError("save-load functionality for graphml is not ready.")
            self._load_graphml(file)
        elif ext == ".graph":
            self._load_pickle(file)
        else:
            raise ValueError(f"Given file has extension: {ext}. Supported extensions: ['.graph']")

    def _save_pickle(self, file):
        serialized_graph = {
            "type": "multidigraph",
            "num_nodes": self.number_of_nodes(),
            "num_edges": self.number_of_edges(),
            "edges": self._edges,
            "node_properties": self._v_props,
            "edge_properties": self._e_props,
            "graph_properties": "todo"
        }
        with open(file, "wb") as graph_file:
            pickle.dump(serialized_graph, graph_file)

    def _load_pickle(self, file):
        with open(file, "rb") as graph_file:
            serialized_graph = pickle.load(graph_file)

        assert serialized_graph["type"] == "multidigraph", f"Expected type of graph to be multidigraph"
        self._nodes = serialized_graph["num_nodes"] - 1
        self._num_edges = serialized_graph["num_edges"]
        self._edges = serialized_graph["edges"]
        self._v_props = serialized_graph["node_properties"]
        self._e_props = serialized_graph["edge_properties"]

        # Construct inv_edges
        for u in self._edges:
            for v in self._edges[u]:
                if v not in self._inv_edges:
                    self._inv_edges[v] = {u}
                else:
                    self._inv_edges[v].add(u)

        # serialized_graph = {
        #     "type": "multidigraph",
        #     "num_nodes": self.number_of_nodes(),
        #     "num_edges": self.number_of_edges(),
        #     "edges": list(self.edges()),
        #     "node_properties": self._v_props,
        #     "edge_properties": self._e_props,
        #     "graph_properties": "todo"
        # }

    def _save_graphml(self, file):
        pass

    def _load_graphml(self, file):
        pass


class NodePropertyMap(dict):
    def __init__(self, graph=None, default=None):
        super(NodePropertyMap, self).__init__()
        self.graph = graph
        self.default = default

    def __repr__(self):
        return f"<NodePropertyMap graph={repr(self.graph)}>"

    def __missing__(self, node):
        if self.graph is None:
            return self.default
        if self.graph.has_node(node):
            return self.default
        raise ValueError(f"[ERROR] NodePropertyMap.__missing__:: {repr(self.graph)} does not contain node {node}.")

    def __getitem__(self, node):
        try:
            return super(NodePropertyMap, self).__getitem__(node)
        except KeyError:
            return self.__missing__(node)


class EdgePropertyMap(dict):
    def __init__(self, graph=None, default=None):
        super(EdgePropertyMap, self).__init__()
        self.graph = graph
        self.default = default

    def __repr__(self):
        return f"<EdgePropertyMap graph={repr(self.graph)}>"

    def __missing__(self, edge):
        if self.graph is None:
            return self.default
        if self.graph.has_edge(edge):
            return self.default
        raise ValueError(f"[ERROR] EdgePropertyMap.__missing__:: {repr(self.graph)} does not contain node {edge}.")

    def __getitem__(self, edge):
        try:
            return dict.__getitem__(self, edge)
        except KeyError:
            return self.__missing__(edge)
