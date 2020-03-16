import { Store } from "pullstate";
import moment from "moment";

export interface PumpState {
  output: number;
}

export interface ValveState {
  position: number;
}

export interface TankState {
  level: number;
  isDraining: boolean;
}

export interface ScaleState {
  value: string;
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
  pumpStates: Map<string, string>;
  valveStates: Map<string, string>;
  tankStates: Map<string, string>;
  scaleState: ScaleState;
}

export const MQTTStore = new Store<MQTTState>({
  isConnected: false,
  mqttInterrupted: false,
  connectionError: undefined
});

export const VosekastStore = new Store<VosekastState>({
  isRunning: false,
  isMeasuring: false,
  isHealthy: false,
  pumpStates: new Map(),
  valveStates: new Map(),
  tankStates: new Map(),
  scaleState: {
    value: ""
  }
});

// reaction that set health state of vosekast negativ if no health message was reported for a long time
VosekastStore.createReaction(
  s => s.lastHealthUpdate,
  healthUpdatedAt => {
    setTimeout(() => {
      VosekastStore.update(s => {
        if (s.lastHealthUpdate === healthUpdatedAt) {
          s.isHealthy = false;
        }
      });
    }, 20000);
  }
);

VosekastStore.createReaction(
  s => s.isHealthy,
  (isHealthy, draft, original, lastIsHealthy) => {
    if (isHealthy !== lastIsHealthy) {
      console.log(
        isHealthy ? "Connected to Vosekast" : "Disconnected from Vosekast"
      );
    }
  }
);

MQTTStore.createReaction(
  s => s.isConnected,
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
