import mqtt from "mqtt";
import { MQTTStore, VosekastStore } from "../Store";
import { message } from "antd";

interface Message {
  type: "status" | "log" | "message" | "command";
  time: string;
}

interface StatusMessage extends Message {
  sensor_id: "scale";
  value1: number;
  unit1: string;
}

export default class MQTTConnector {
  client: mqtt.MqttClient;

  constructor(url: string, username?: string, password?: string) {
    const options: mqtt.IClientOptions = {};
    if (username != null) options.username = username;
    if (password != null) options.password = password;

    this.client = mqtt.connect(url, options);

    this.client.on("connect", this.handleConnect);
    this.client.on("message", this.handleMessage);
    this.client.on("subscribe", this.handleSubscription);
    this.client.on("close", this.handleDissconnect);
    this.client.on("error", this.handleError);
    this.client.on("offline", this.handleOffline);
  }

  handleConnect = () => {
    MQTTStore.update(s => {
      s.isConnected = true;
      s.connectionError = undefined;
      s.mqttInterrupted = false;
    });

    console.log("Connect to MQTT Broker!");
    this.client.subscribe("vosekast/#");
  };

  handleMessage = (
    topic: string,
    payload: Buffer | string,
    packet: mqtt.Packet
  ) => {
    const message: Message = JSON.parse(payload as string);

    switch (message.type) {
      case "status":
        this.handleStatusMessage(message as StatusMessage);
        break;
      case "log":
        break;
      case "message":
        break;
      case "command":
        break;
    }
  };

  handleSubscription = (err: Error, granted: mqtt.ISubscriptionGrant[]) => {
    message.success("Connect to Vosekast Info Stream!");
    console.log("Subscribed to vosekast topics.");
  };

  handleDissconnect = () => {
    MQTTStore.update(s => {
      s.isConnected = false;
    });
  };

  handleError = (error: Error) => {
    MQTTStore.update(s => {
      s.connectionError = error;
    });

    message.error("MQTT Connection Error");
    console.error(error.message);
  };

  handleOffline = () => {
    MQTTStore.update(s => {
      s.mqttInterrupted = true;
    });

    message.warning("MQTT Connection Lost. Try to reconnect.");
  };

  handleStatusMessage = (message: StatusMessage) => {
    switch (message.sensor_id) {
      case "scale":
        VosekastStore.update(s => {
          s.scaleState.value = message.value1;
          s.scaleState.unit = message.unit1;
        });
        break;
    }
  };
}
