from abc import ABC, abstractmethod


class TSGenerator(ABC):
    TURN_BASED = True
    DETERMINISTIC = True
    QUALITATIVE = True

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

    # noinspection PyMethodMayBeStatic
    def state_properties(self):
        """
        Properties of states in transition system.
        :return: A dictionary of type: {<pname>: <default-value>}
        """
        return dict()

    # noinspection PyMethodMayBeStatic
    def transition_properties(self):
        """
        Properties of transition in transition system.
        :return: A dictionary of type:
            {
                "pname": {
                            "default": <value>,
                            "values": {
                                        (<state>, <action>, <state>): <property value>
                                      }
                         }
            }
        """
        return dict()
