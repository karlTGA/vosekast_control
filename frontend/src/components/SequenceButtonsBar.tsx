import React from "react";
import { Button } from "antd";
import {
  CaretRightOutlined,
  PauseOutlined,
  BorderOutlined,
} from "@ant-design/icons";

export default function SequenceButtonsBar() {
  return (
    <div className="sequence-buttons-bar">
      <div className="current-sequence-info">{`Current Sequence: 123456678`}</div>
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
