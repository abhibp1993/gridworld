import itertools
from gridworld import Gridworld, graphify
from gw_utils import *


class StochasticGridworld(Gridworld):
    """
    `StochasticGridworld` represents a qualitative, stochastic gridworld with no obstacles and one player.

    To define a gridworld, user must implement the following abstract methods:
        * states
        * actions
        * delta

    and optionally implement any other methods such as `atoms, label`.

    In comparison with `det_gw/SimpleGridworld` class, only the `delta` method is different in this case.
    There are two options to mark the gridworld as stochastic:
        * Define `__init__` function and set `self.deterministic = False` after a call to `super(...).__init__(...)`.
        * Pass `deterministic = False` during object creation.
    """
    def __init__(self, dim, deterministic=False, qualitative=True, turn_based=True,
                 obs_type=GW_OBS_TYPE_SINK, boundary_type=GW_BOUNDARY_TYPE_BOUNCY):
        super(StochasticGridworld, self).__init__(dim, deterministic=deterministic, qualitative=qualitative,
                                                  turn_based=turn_based, obs_type=obs_type, boundary_type=boundary_type)
        self.deterministic = False
        self.qualitative = True

    def states(self):
        """
        The set of states in gridworld.
        In this example, a state is the position of player in the gridworld: `(p1.row, p1.col)`

        :return: Iterable over states.
        """
        rows, cols = self.dim
        return set(itertools.product(range(rows), range(cols)))

    def actions(self):
        """
        The set of actions in gridworld.

        :return: Iterable[str]
        """
        return set(GW_ACT_4.keys())

    def delta(self, state, act):
        """
        Transition function of gridworld.

        :param state: An element from self.states().
        :param act: An element from self.actions().
        :return: An element from self.states().

        :note: Since the gridworld is deterministic, this function must return a single state.
        """
        # Decouple state
        row, col = state

        # Get action function (standard functions are implemented in gridworld2.py)
        act_func = GW_ACT_4[act]

        # Apply action to state
        n_row, n_col = act_func(row, col)

        # Validate new state is within boundary
        n_row, n_col = bouncy_boundary(n_row, n_col, self.dim)

        # Return state
        return [(n_row, n_col)]

    def atoms(self):
        return {'goal'}

    def label(self, state):
        if state == (3, 3):
            return {'goal'}
        return set()


if __name__ == '__main__':
    # Create an object of generator class
    gw = StochasticGridworld(dim=(5, 5))
    print(repr(gw))

    # Graphify gridworld
    gw_graph = graphify(gw)

