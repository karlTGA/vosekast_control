import React from "react";
import { Tag } from "antd";
import { VosekastStore } from "../Store";
import { useStoreState } from "pullstate";

export function ScaleTag() {
  const scaleState = useStoreState(VosekastStore, s => s.scaleState);
  if (scaleState == null) return <></>;

  return <Tag>Scale: {scaleState.value}</Tag>;
}
