import { Store } from "pullstate";

export interface state {
  isConnected: boolean;
  isRunning: boolean;
  isMeasuring: boolean;
}

export const UIStore = new Store<state>({
  isConnected: false,
  isRunning: false,
  isMeasuring: false
});
