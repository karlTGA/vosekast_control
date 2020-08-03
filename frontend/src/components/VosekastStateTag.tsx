import React, { useEffect } from "react";
import { Tag } from "antd";
import { useStoreState } from "pullstate";
import { VosekastStore } from "../Store";
import MQTTConnection from "../utils/MQTTConnection";

export default function VosekastStateTag() {
  const appControlState = useStoreState(
    VosekastStore,
    (s) => s.appControlState
  );

  useEffect(() => {
    const requestCurrentState = async () => {
      MQTTConnection.publishCommand(
        "system",
        "app_control",
        "request_current_app_state"
      );
    };

    requestCurrentState();
  }, []);

  return <Tag>{appControlState}</Tag>;
}
