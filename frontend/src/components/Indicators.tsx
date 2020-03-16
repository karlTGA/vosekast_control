import React from "react";
import { useStoreState } from "pullstate";
import { Alert, Tag } from "antd";
import {
  CheckCircleTwoTone,
  ExclamationCircleTwoTone
} from "@ant-design/icons";
import { MQTTStore, VosekastStore } from "../Store";

export function OnlineIndicator({ isConnected }: { isConnected: boolean }) {
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

export function MQTTOnlineIndicator() {
  const isConnected = useStoreState(MQTTStore, s => s.isConnected);
  return OnlineIndicator({ isConnected });
}

export function VosekastOnlineIndicator() {
  const isConnected = useStoreState(VosekastStore, s => s.isHealthy);
  return OnlineIndicator({ isConnected });
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
