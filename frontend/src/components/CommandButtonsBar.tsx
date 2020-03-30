import React from "react";
import { PumpButton } from "./Pump";
import { Button } from "antd";
import classNames from "classnames";
import { ValveButton } from "./Valve";

export default function CommandButtonsBar() {
  return (
    <>
      <PumpButton pumpId="pump_measuring_tank" title="Pump Measuring Tank" />
      <PumpButton pumpId="pump_constant_tank" title="Pump Constant Tank" />
      <ValveButton
        valveId="measuring_drain_valve"
        title="Measuring Tank Drain Valve"
      />
      <ValveButton
        valveId="measuring_tank_switch"
        title="Measuring Tank Fill Valve"
      />
    </>
  );
}

export function CommandButton({
  isActive,
  imagePath,
  title,
  onClick
}: {
  isActive: boolean;
  imagePath: string;
  title: string;
  onClick: () => void;
}) {
  return (
    <Button
      className={classNames("device-command-button", {
        "device-deactivated": !isActive
      })}
      onClick={onClick}
    >
      <img src={imagePath} alt="" />
      {title}
    </Button>
  );
}
