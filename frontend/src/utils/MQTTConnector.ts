import mqtt from "mqtt";
import { MQTTStore, VosekastStore } from "../Store";
import { message } from "antd";
import moment from "moment";

interface Message {
  type: "status" | "log" | "message" | "command";
  time: string;
}

interface StatusMessage extends Message {
  sensor_id: "scale" | "system";
  value1: number | string;
  unit1: string;
}

interface LogMessage extends Message {
  sensor_id: "Pump" | "Valve";
  message: string;
  level: "INFO" | "DEBUG" | "WARNING" | "ERROR";
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
        this.handleLogMessage(message as LogMessage);
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
          s.scaleState.value = message.value1 as number;
          s.scaleState.unit = message.unit1;
        });
        break;
      case "system":
        if (message.value1 === "OK") {
          VosekastStore.update(s => {
            s.isHealthy = (message.value1 as string) === "OK";
            s.lastHealthUpdate = moment();
          });
        }
        break;
      default:
        console.log(`Receive unknown message: ${JSON.stringify(message)}`);
    }
  };

  handleLogMessage = (message: LogMessage) => {
    const combinedMessage = `${message.sensor_id}: ${message.message}`;

    switch (message.level) {
      case "DEBUG":
        console.debug(combinedMessage);
        break;
      case "ERROR":
        console.error(combinedMessage);
        break;
      case "INFO":
        console.info(combinedMessage);
        break;
      case "WARNING":
        console.warn(combinedMessage);
        break;
    }
  };
}
