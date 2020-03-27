import mqtt from "mqtt";
import { MQTTStore, VosekastStore } from "../Store";
import { message } from "antd";
import moment from "moment";

interface Message {
  type: "status" | "log" | "message" | "command";
  time: string;
}

interface StatusMessage extends Message {
  device_type: "scale" | "system" | "pump" | "valve";
  device_id: string;
  new_state: string;
}

interface LogMessage extends Message {
  sensor_id: "Pump" | "Valve";
  message: string;
  level: "INFO" | "DEBUG" | "WARNING" | "ERROR";
}

class MQTTConnector {
  client?: mqtt.MqttClient;
  private connectionOptions: mqtt.IClientOptions = {};
  private host: string = "";

  constructor(url: string, username?: string, password?: string) {
    if (username != null) this.connectionOptions.username = username;
    if (password != null) this.connectionOptions.password = password;
    this.host = url;
  }

  connect = () => {
    this.client = mqtt.connect(this.host, this.connectionOptions);

    this.client.on("connect", this.handleConnect);
    this.client.on("message", this.handleMessage);
    this.client.on("close", this.handleDissconnect);
    this.client.on("error", this.handleError);
    this.client.on("offline", this.handleOffline);
  };

  handleConnect = () => {
    if (this.client != null) {
      MQTTStore.update(s => {
        s.isConnected = true;
        s.connectionError = undefined;
        s.mqttInterrupted = false;
      });

      this.client.subscribe("vosekast/#", { qos: 0 }, this.handleSubscription);
    }
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
    if (err == null) {
      message.success("Connect to Vosekast Info Stream!");
      console.log("Subscribed to vosekast topics.");
    }
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
    switch (message.device_type) {
      case "scale":
        VosekastStore.update(s => {
          s.scaleState.value = message.new_state;
        });
        break;
      case "system":
        if (message.device_id === "health" && message.new_state === "OK") {
          VosekastStore.update(s => {
            s.isHealthy = message.new_state === "OK";
            s.lastHealthUpdate = moment();
          });
        }
        break;
      case "pump":
        VosekastStore.update(s => {
          s.pumpStates.set(message.device_id, message.new_state);
        });
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

// export singleton for reusing of the connection
const MQTTConnection = new MQTTConnector("ws://localhost:9001");
export default MQTTConnection;
