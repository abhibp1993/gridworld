import itertools
from tsgen import TSGenerator
from gw_utils import GW_ACT_4, bouncy_boundary


class SimpleGridworld(TSGenerator):
    """
    `SimpleGridworld` represents a gridworld with no obstacles and one player.
    By default, the gridworld is deterministic.

    To define a gridworld, user must implement the following methods:
        * `dim` method that returns a 2-tuple: (num_rows, num_cols)

    in addition to the following abstract methods:
        * states
        * actions
        * delta

    and optionally implement any other methods such as `atoms, label`.
    """
    # noinspection PyMethodMayBeStatic
    def dim(self):
        return 5, 5

    def states(self):
        """
        The set of states in gridworld.
        In this example, a state is the position of player in the gridworld: `(p1.row, p1.col)`

        :return: Iterable over states.
        """
        rows, cols = self.dim()
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
        n_row, n_col = bouncy_boundary(n_row, n_col, self.dim())

        # Return state
        return n_row, n_col

    def atoms(self):
        return {'goal'}

    def label(self, state):
        if state == (3, 3):
            return {'goal'}
        return set()


if __name__ == '__main__':
    from gridworld2 import Gridworld

    # Create an object of generator class
    tsgen = SimpleGridworld()

    # Construct a gridworld
    gw = Gridworld(tsgen=tsgen)
    print(repr(gw))
