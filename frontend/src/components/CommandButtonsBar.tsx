import React from "react";
import { PumpButton } from "./Pump";

const CommandButtonsBar = () => {
  return (
    <>
      <PumpButton pumpId="pump_measuring_tank" title="Pump Measuring Tank" />
    </>
  );
};

export default CommandButtonsBar;
