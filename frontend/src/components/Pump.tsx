import React from "react";
import { Button, Tag } from "antd";
import { VosekastStore } from "../Store";
import { useStoreState } from "pullstate";
import classNames from "classnames";
import { CommandButton } from "./CommandButtonsBar";

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
  const isDeactivated = pumpState == null;

  function handlePumpToggle() {
    console.log("Try to activate pump");
  }

  return (
    <CommandButton
      title={title}
      imagePath="/img/icons/manufacturing/017-pump.svg"
      isActive={!isDeactivated}
      onClick={handlePumpToggle}
    />
  );
}
