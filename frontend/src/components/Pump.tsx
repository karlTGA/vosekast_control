import React from "react";
import { Tag } from "antd";
import { VosekastStore } from "../Store";
import { useStoreState } from "pullstate";

export function PumpTag({ pumpId }: { pumpId: string }) {
  const pumpState = useStoreState(VosekastStore, s => s.pumpStates.get(pumpId));

  return (
    <Tag>
      Pump {pumpId}: {pumpState != null ? pumpState.output : "Unknown"}
    </Tag>
  );
}
