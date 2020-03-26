import React from "react";
import { Button, Tag } from "antd";
import { VosekastStore } from "../Store";
import { useStoreState } from "pullstate";
import classNames from "classnames";

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
  const isActivated = pumpState != null && pumpState === "Activated";

  return (
    <Button
      className={classNames("device-command-button", {
        "device-activated": isActivated
      })}
    >
      {title}
    </Button>
  );
}
