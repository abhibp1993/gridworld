# Gridworld 

The library provides an interface to create a gridworld as a graph transition system.

*The library is under development. Here are some tips to start using it.* 


# Development Idea

There are three important classes: `Graph, Gridworld` and `TSGenerator`. 


**Graph**: The `Graph` class defines a custom (python) implementation of graph
that is more efficient than `networkx`. The efficiency comes at the cost that nodes, 
edges cannot be removed. Instead, a `SubGraph` can be constructed by defining filters
on nodes, edges. 

Also, we define `NodePropertyMap, EdgePropertyMap` classes that efficiently store 
properties associated with nodes and edges. The classes provide an interface 
to define a `default` value for the property.  

**Gridworld**: Gridworld class defined procedures to construct a transition system graph
from a `TSGenerator` object. 

> **_NOTE:_**  The user should **NOT** modify `Gridworld, Graph` classes.


## Creating Gridworld

User must complete two steps to define gridworld. 
1. Define gridworld transition system.
2. Construct gridworld. 


### Defining Gridworld 

The user should extend `TSGenerator` class by defining the functions given below. 
See `examples/` folder for examples. 


**MUST BE IMPLEMENTED FUNCTIONS**
* `dim()`: returns a 2-tuple of `(num_rows, num_cols)` defining the dimension of the gridworld.
* `states()`: returns the set of states. 
* `actions()`: returns the set of actions. 
* `delta(state, act)`: defines the transition function depending on following options
  * If gridworld is deterministic: return a single state. 
  * If gridworld is qualitative, stochastic: return a set of states. 
  * If gridworld is quantitative, stochastic: return a set of 2-tuples: `(state, prob)`

**OPTIONAL FUNCTIONS** 
* `atoms()`: returns a set of atomic propositions. 
* `label(state)`: returns a set of atomic propositions true in given state. 


### Example: SimpleGridworld

For example, here is a snippet from `examples/simple_gw.py` which defines a deterministic
gridworld with one player and no obstacles.

*Note: `GW_ACT_4` is a set of standard 4-connecting actions and 
`bouncy_boundary` is a utility function defined in `gw_utils.py`.* 

```python
class SimpleGridworld(TSGenerator):
    def dim(self):
        return 5, 5

    def states(self):
        rows, cols = self.dim()
        return set(itertools.product(range(rows), range(cols)))

    def actions(self):
        return set(GW_ACT_4.keys())

    def delta(self, state, act):
        # Decouple state
        row, col = state

        # Get action function (standard functions are implemented in gridworld2.py)
        act_func = GW_ACT_4[act]

        # Apply action to state
        n_row, n_col = act_func(row, col)

        # Validate new state is within boundary
        n_row, n_col = bouncy_boundary(n_row, n_col, self.dim())

        # Return state
        return n_row, n_col

    def atoms(self):
        return {'goal'}

    def label(self, state):
        if state == (3, 3):
            return {'goal'}
        return set()
```

### Construct Gridworld

The steps to construct a gridworld transition system are
1. Create an instance of extended class:
    ```python
    tsgen = SimpleGridworld()
    ```

2. Create gridworld object with this instance.
   ```python
   from gridworld2 import Gridworld 
   gw = Gridworld(tsgen)
   ```
   
Internally, `gw` object is a `graph.Graph` with additional properties. 