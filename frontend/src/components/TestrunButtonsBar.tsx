import React from "react";
import { Button } from "antd";
import {
  CaretRightOutlined,
  PauseOutlined,
  BorderOutlined,
} from "@ant-design/icons";
import { TestrunInfos } from "../Store";
import MQTTConnection from "../utils/MQTTConnection";

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

export default function TestrunButtonsBar({
  testrun,
}: {
  testrun?: TestrunInfos;
}) {
  return (
    <div className="sequence-buttons-bar">
      <div className="current-sequence-info">
        {testrun != null
          ? `Current Testrun: ${testrun.id}`
          : "No testrun running."}
      </div>
      <Button onClick={startRun}>
        <CaretRightOutlined />
        Start
      </Button>
      <Button onClick={stopRun}>
        <BorderOutlined />
        Stop
      </Button>
      <Button onClick={pauseRun}>
        <PauseOutlined />
        Pause
      </Button>
    </div>
  );
}
