import pydux
from copy import deepcopy

class VosekastStore():

    def __init__(self, vosekast):
        self.vosekast = vosekast


        def reducer(state, action):
            if action is None or action.get('type') is None:
                return state
            else:
                newState = deepcopy(state)

                if action.get('body') is None:
                    return newState
                else:
                    if action['type'] == 'Update Pump Measuring Tank':
                        newState["Pump Measuring Tank"] = deepcopy(action.get('body'))
                        return newState
                    elif action['type'] == 'Update Pump Base Tank':
                        newState["Pump Base Tank"] = deepcopy(action.get('body'))
                        return newState
                    elif action['type'] == 'UPDATE_SCALE':
                        newState["Scale"] = deepcopy(action.get('body'))
                        return newState

                    else:
                        return newState

        default_state = {
            "Pump Measuring Tank":{
                "State": 0
            },
            "Pump Base Tank": {
                "State": 0
            },
            "Scale":{
                "State": 0,
                "Value": 0,
                "123": 0,
                "456": 0
            }
        }

        self._store = pydux.create_store(reducer, default_state)

    def dispatch(self, action):
        return self._store.dispatch(action)

    def get_state(self):
        return self._store.get_state()

    def subscribe(self, listener):
        return self._store.subscribe(listener)
