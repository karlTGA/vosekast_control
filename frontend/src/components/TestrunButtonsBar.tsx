import React from "react";
import { Button } from "antd";
import {
  CaretRightOutlined,
  PauseOutlined,
  BorderOutlined,
} from "@ant-design/icons";
import { TestrunInfos } from "../Store";

export default function SequenceButtonsBar({
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
      <Button>
        <CaretRightOutlined />
        Start
      </Button>
      <Button>
        <BorderOutlined />
        Stop
      </Button>
      <Button>
        <PauseOutlined />
        Pause
      </Button>
    </div>
  );
}
