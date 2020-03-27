import React from "react";
import { Tag } from "antd";
import { VosekastStore } from "../Store";
import { useStoreState } from "pullstate";
import { CommandButton } from "./CommandButtonsBar";
import MQTTConnection from "../utils/MQTTConnection";

interface PumpActionProps {
  pumpId: string;
  title: string;
}

export function PumpTag({ pumpId, title }: PumpActionProps) {
  const pumpState = useStoreState(VosekastStore, s => s.pumpStates.get(pumpId));

  return (
    <Tag>
      {title}: {pumpState != null ? pumpState : "Unknown"}
    </Tag>
  );
}

export function PumpButton({ pumpId, title }: PumpActionProps) {
  const pumpState = useStoreState(VosekastStore, s => s.pumpStates.get(pumpId));
  const isActive = pumpState === "RUNNING";

  function handlePumpToggle() {
    MQTTConnection.publishCommand("pump", pumpId, isActive ? "stop" : "start");
  }

  return (
    <CommandButton
      title={title}
      imagePath="/img/icons/manufacturing/017-pump.svg"
      isActive={isActive}
      onClick={handlePumpToggle}
    />
  );
}
