import React from "react";
import { Tag } from "antd";
import { useStoreState } from "pullstate";
import { VosekastStore } from "../Store";

export default function VosekastStateTag() {
  const appControlState = useStoreState(
    VosekastStore,
    (s) => s.appControlState
  );
  return <Tag>{appControlState}</Tag>;
}
