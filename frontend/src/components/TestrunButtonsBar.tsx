import React from "react";
import { Button } from "antd";
import {
  CaretRightOutlined,
  PauseOutlined,
  BorderOutlined,
} from "@ant-design/icons";
import { TestrunInfos } from "../Store";
import MQTTConnection from "../utils/MQTTConnection";
import { ScaleTag } from "./Scale";



function startRun() {
  MQTTConnection.publishCommand("system", "testrun_controller", "start_run");
}

function stopRun() {
  MQTTConnection.publishCommand(
    "system",
    "testrun_controller",
    "stop_current_run"
  );
}

function pauseRun() {
  MQTTConnection.publishCommand(
    "system",
    "testrun_controller",
    "pause_current_run"
  );
}

function shutdownVosekast() {
  MQTTConnection.publishCommand("system", "main", "shutdown");
}

export default function TestrunButtonsBar({
  testrun,
}: {
  testrun?: TestrunInfos;
}) {
  return (
    <div className="sequence-buttons-bar">
      <div className="info-tag">
        {testrun != null
          ? `Current Testrun: ${testrun.id}`
          : "No testrun running."}
      </div>
      <Button
        onClick={startRun}
        disabled={
          testrun != null &&
          (testrun.state === "MEASURING" || testrun.state === "WAITING")
        }
      >
        <CaretRightOutlined />
        Start
      </Button>
      <Button
        onClick={stopRun}
        disabled={testrun == null || testrun.state === "PAUSED"}
      >
        <BorderOutlined />
        Stop
      </Button>
      <Button
        onClick={pauseRun}
        disabled={testrun == null || testrun.state === "STOPPED"}
      >
        <PauseOutlined />
        Pause
      </Button>
      <Button onClick={shutdownVosekast}>Shutdown</Button>
      <div className="vl" />
      <ScaleTag />
    </div>
  );
}
