import React from "react";
import { useStoreState } from "pullstate";
import { Alert } from "antd";
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from "@ant-design/icons";
import { MQTTStore, VosekastStore } from "../Store";

export function OnlineIndicator({
  isConnected,
  connectText = "Connected",
  dissconnectText = "Dissconnect"
}: {
  isConnected: boolean;
  connectText?: string;
  dissconnectText?: string;
}) {
  return (
    <>
      {isConnected ? (
        <div className="indicator indicator-success">
          <CheckCircleOutlined /> {connectText}
        </div>
      ) : (
        <div className="indicator indicator-error">
          <ExclamationCircleOutlined /> {dissconnectText}
        </div>
      )}
    </>
  );
}

export function MQTTOnlineIndicator() {
  const isConnected = useStoreState(MQTTStore, s => s.isConnected);
  return OnlineIndicator({
    isConnected,
    connectText: "MQTT",
    dissconnectText: "MQTT"
  });
}

export function VosekastOnlineIndicator() {
  const isConnected = useStoreState(VosekastStore, s => s.isHealthy);
  return OnlineIndicator({
    isConnected,
    connectText: "Vosekast",
    dissconnectText: "Vosekast"
  });
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
