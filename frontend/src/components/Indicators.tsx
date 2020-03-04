import React from "react";
import { useStoreState } from "pullstate";
import { Alert, Tag } from "antd";
import {
  CheckCircleTwoTone,
  ExclamationCircleTwoTone
} from "@ant-design/icons";
import { MQTTStore } from "../Store";

export function OnlineIndicator() {
  const isConnected = useStoreState(MQTTStore, s => s.isConnected);
  return (
    <>
      {isConnected ? (
        <Tag color="success">
          <CheckCircleTwoTone twoToneColor="#52c41a" /> Connected
        </Tag>
      ) : (
        <Tag color="warning">
          <ExclamationCircleTwoTone twoToneColor="#fcba03" /> Dissconnected
        </Tag>
      )}
    </>
  );
}

export function ErrorIndicator() {
  const connectionError = useStoreState(MQTTStore, s => s.connectionError);

  return (
    <>
      {connectionError != null && (
        <Alert
          className="fixed-banner"
          type="error"
          message="MQTT Connection Error"
          description={connectionError.message}
          banner
          showIcon
        />
      )}
    </>
  );
}
