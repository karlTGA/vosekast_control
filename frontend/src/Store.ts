import { Store } from "pullstate";
import moment from "moment";
import { TimeSeries } from "pondjs";

export type PumpState = "STOPPED" | "RUNNING" | "UNKNOWN";
export type ValveState = "OPEN" | "CLOSED" | "UNKNOWN";
export type TankState =
  | "UNKNOWN"
  | "DRAINED"
  | "EMPTY"
  | "FILLED"
  | "PAUSED"
  | "STOPPED"
  | "IS_DRAINING"
  | "IS_FILLING";
export type Commands =
  | "start"
  | "stop"
  | "toggle"
  | "close"
  | "open"
  | "drain_tank"
  | "prepare_to_fill"
  | "shutdown"
  | "clean"
  | "start_run"
  | "stop_current_run";

export interface ScaleState {
  value: string;
}

export interface TestrunInfos {
  id: string;
  startedAt: number;
  createdAt: number;
  state: string;
  emulated: boolean | null;
  results?: TimeSeries;
}

export interface MQTTState {
  isConnected: boolean;
  connectionError?: Error;
  mqttInterrupted: boolean;
}

export interface VosekastState {
  isHealthy: boolean;
  lastHealthUpdate?: moment.Moment;
  isRunning: boolean;
  isMeasuring: boolean;
  appControlState: string;
  pumpStates: Map<string, PumpState>;
  valveStates: Map<string, ValveState>;
  tankStates: Map<string, TankState>;
  scaleState: ScaleState;
  testruns: Map<string, TestrunInfos>;
}

export const MQTTStore = new Store<MQTTState>({
  isConnected: false,
  mqttInterrupted: false,
  connectionError: undefined,
});

export const VosekastStore = new Store<VosekastState>({
  isRunning: false,
  isMeasuring: false,
  isHealthy: false,
  appControlState: "UNKNOWN",
  pumpStates: new Map(),
  valveStates: new Map(),
  tankStates: new Map(),
  scaleState: {
    value: "",
  },
  testruns: new Map(),
});

// reaction that set health state of vosekast negativ if no health message was reported for a long time
VosekastStore.createReaction(
  (s) => s.lastHealthUpdate,
  (healthUpdatedAt) => {
    setTimeout(() => {
      VosekastStore.update((s) => {
        if (s.lastHealthUpdate === healthUpdatedAt) {
          s.isHealthy = false;
        }
      });
    }, 20000);
  }
);

VosekastStore.createReaction(
  (s) => s.isHealthy,
  (isHealthy, draft, original, lastIsHealthy) => {
    if (isHealthy !== lastIsHealthy) {
      console.log(
        isHealthy ? "Connected to Vosekast" : "Disconnected from Vosekast"
      );
    }
  }
);

MQTTStore.createReaction(
  (s) => s.isConnected,
  (isConnected, draft, original, lastIsConnected) => {
    if (isConnected !== lastIsConnected) {
      console.log(
        isConnected
          ? "Connected to MQTT Broker"
          : "Disconnected from MQTT Broker"
      );
    }
  }
);
