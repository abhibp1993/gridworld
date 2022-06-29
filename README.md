# Gridworld 

The library provides an interface to create a gridworld as a graph transition system.
Following three types of gridworld can be generated with the same API.
* Deterministic Gridworld
* Stochastic Gridworld (Qualitative: Edge (s, a, s') is included if Pr(s'| s, a) > 0).
* Stochastic Gridworld (Quantitative: Each transition is marked with probability value between 0 and 1).


*The library is under development. Here are some tips to start using it.* 


## How to use?

A gridworld is defined by extending the class `Gridworld`. The user must implement the following methods:
* `states()`: The set of states. 
* `actions()`: The set of actions. 
* `delta(state, act)`: Depending on the type of gridworld, one of the following output is expected.
  * If gridworld is deterministic: return a single state. 
  * If gridworld is qualitative, stochastic: return a set of states. 
  * If gridworld is quantitative, stochastic: return a set of 2-tuples: `(state, prob)`

The following methods are optional. 
* `atoms()`: returns a set of atomic propositions. 
* `label(state)`: returns a set of atomic propositions true in given state. 

A gridworld graph is constructed as follows:
```python
# Create an instance of extended class (say MyGridworld). 
gw = MyGridworld(dim=(5, 5))
graph = graphify(gw)
```

The generated graph is an object of type `graph.Graph`. 


## Graph Class

The `Graph` class defines a custom (python) implementation of multi-digraph
that is slightly efficient than `networkx`. The efficiency comes at the cost that nodes, 
edges cannot be removed. Instead, a `SubGraph` can be constructed by defining filters
on nodes, edges. (Note: `SubGraph` is not yet implemented in the library.)

In addition, we store node, edge properties separately using `NodePropertyMap, EdgePropertyMap` classes.
The motivation behind this is that the winning regions, strategies etc. can be viewed as node, edge properties.
By decoupling the properties from graph representation, it is possible to store them separately. 
Moreover, `NodePropertyMap, EdgePropertyMap` are implemented as default dictionary, which saves space 
by storing only the non-default values. 

The `Graph` object can be saved/loaded by using `Graph.save()` and `Graph.load()` functions. Note that 
the saving to `.graph` file is currently supported (internally, `.graph` uses pickle protocol).

**Note:** Currently, `Graph` class implements limited functionality. In case more functionality is needed, 
use the `to_nx_graph()` function to generate a `networkx.MultiDiGraph` object. 


