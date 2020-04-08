import React from "react";
import { Tag } from "antd";
import { VosekastStore } from "../Store";
import { useStoreState } from "pullstate";
import { CommandButton } from "./CommandButton";
import MQTTConnection from "../utils/MQTTConnection";

interface ValveActionProps {
  valveId: string;
  title: string;
}

export function ValveTag({ valveId, title }: ValveActionProps) {
  const valveState = useStoreState(VosekastStore, (s) =>
    s.valveStates.get(valveId)
  );

  return (
    <Tag>
      {title}: {valveState != null ? valveState : "Unknown"}
    </Tag>
  );
}

export function ValveButton({ valveId, title }: ValveActionProps) {
  const valveState = useStoreState(VosekastStore, (s) =>
    s.valveStates.get(valveId)
  );
  const isActive = valveState === "OPEN";

  function handleValveToggle() {
    MQTTConnection.publishCommand(
      "valve",
      valveId,
      isActive ? "close" : "open"
    );
  }

  return (
    <CommandButton
      title={title}
      imagePath="/img/icons/manufacturing/005-valve.svg"
      isActive={isActive}
      onClick={handleValveToggle}
    />
  );
}
