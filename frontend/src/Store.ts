import { Store } from "pullstate";

export interface MQTTState {
  isConnected: boolean;
  connectionError?: Error;
  mqttInterrupted: boolean;
}

export interface VosekastState {
  isRunning: boolean;
  isMeasuring: boolean;
}

export const MQTTStore = new Store<MQTTState>({
  isConnected: false,
  mqttInterrupted: false,
  connectionError: undefined
});

export const VosekastStore = new Store<VosekastState>({
  isRunning: false,
  isMeasuring: false
});
