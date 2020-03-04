import { Store } from "pullstate";

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
  value: number;
  unit: string;
}

export interface MQTTState {
  isConnected: boolean;
  connectionError?: Error;
  mqttInterrupted: boolean;
}

export interface VosekastState {
  isRunning: boolean;
  isMeasuring: boolean;
  pumpStates: Map<string, PumpState>;
  valveStates: Map<string, ValveState>;
  tankStates: Map<string, TankState>;
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
  pumpStates: new Map(),
  valveStates: new Map(),
  tankStates: new Map(),
  scaleState: {
    value: -1,
    unit: ""
  }
});
