import React from "react";
import { PumpButton } from "./Pump";
import { ValveButton } from "./Valve";

export default function DeviceButtonsBar() {
  return (
    <>
      <PumpButton pumpId="pump_measuring_tank" title="Pump Measuring Tank" />
      <PumpButton pumpId="pump_constant_tank" title="Pump Constant Tank" />
      <ValveButton
        valveId="measuring_drain_valve"
        title="Measuring Tank Drain Valve"
      />
      <ValveButton
        valveId="measuring_bypass_valve"
        title="Measuring Bypass Valve"
      />
      <ValveButton
        valveId="measuring_tank_switch"
        title="Measuring Tank Fill Valve"
      />
    </>
  );
}
