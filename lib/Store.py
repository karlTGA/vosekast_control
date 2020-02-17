import pydux
from copy import deepcopy


class VosekastStore:
    def __init__(self, vosekast):
        """ All the values which interest us are stored in this store . The
        checkboxes are created according to this store. It can only be changed
        by means of the dispatch-function.
        """
        self.vosekast = vosekast

        def reducer(state, action):
            if action is None or action.get("type") is None:
                return state
            else:
                newState = deepcopy(state)

                if action.get("body") is None:
                    return newState
                else:
                    if action["type"] == "Update Pump Measuring Tank":
                        newState["Pump Measuring Tank"] = deepcopy(action.get("body"))
                        return newState
                    elif action["type"] == "Update Pump Constant Tank":
                        newState["Pump Constant Tank"] = deepcopy(action.get("body"))
                        return newState
                    elif action["type"] == "UPDATE_SCALE":
                        newState["Scale"] = deepcopy(action.get("body"))
                        return newState
                    elif action["type"] == "Update Measuring Drain Valve":
                        newState["Measuring Drain Valve"] = deepcopy(action.get("body"))
                        return newState
                    elif action["type"] == "Update Measuring Tank Switch":
                        newState["Measuring Tank Switch"] = deepcopy(action.get("body"))
                        return newState

        default_state = {
            "Pump Measuring Tank": {"State": 0},
            "Pump Constant Tank": {"State": 0},
            "Scale": {"State": 0, "Value": 0},
            "Measuring Drain Valve": {"State": 5},
            "Measuring Switch Valve": {"State": 5},
        }

        self._store = pydux.create_store(reducer, default_state)

    def dispatch(self, action):
        return self._store.dispatch(action)

    def get_state(self):
        return self._store.get_state()

    def subscribe(self, listener):
        return self._store.subscribe(listener)
