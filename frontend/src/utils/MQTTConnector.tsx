import mqtt from "mqtt";
import { MQTTStore } from "../Store";
import { message } from "antd";

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

    message.success("Connecto to MQTT Broker!");
  };

  handleMessage = (topic: string, payload: Buffer, packet: mqtt.Packet) => {
    debugger;
  };

  handleSubscription = (err: Error, granted: mqtt.ISubscriptionGrant[]) => {
    debugger;
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
}
