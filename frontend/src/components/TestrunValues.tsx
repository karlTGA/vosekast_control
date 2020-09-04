import React from "react";
import { TestrunInfos } from "../Store";
import { TimeEvent } from "pondjs";
import { Card } from "antd";

interface ValueProps {
  title: string;
  imagePath: string;
}

const valueMapping: Record<string, ValueProps> = {
  scaleValue: {
    title: "Scale in kg",
    imagePath: "/img/icons/manufacturing/025-meter.svg",
  },
  flowValue: {
    title: "Flow in l/min",
    imagePath: "/img/icons/manufacturing/020-planning.svg",
  },
};

function TestrunValueCard({
  valueKey,
  timeEvent,
}: {
  valueKey: string;
  timeEvent: TimeEvent;
}) {
  const valueProps = valueMapping[valueKey];
  const value = Math.round(timeEvent.get(valueKey) * 1000) / 1000;

  return (
    <Card className="testrun_value_card" key={valueKey}>
      <div className="testrun_value_card_icon">
        <img src={valueProps.imagePath} alt={"valueKey"} />
      </div>
      <div className="testrun_value_card_text">
        <div className="testrun_value_card_title">{valueProps.title} </div>
        <div className="testrun_value_card_value">{value}</div>
      </div>
    </Card>
  );
}

export default function TestrunValues({
  testrun,
}: {
  testrun: TestrunInfos | undefined;
}) {
  if (testrun == null || testrun.results == null) return <></>;
  const keys = Object.keys(valueMapping);
  const timeEvent = testrun.results.atLast();

  return (
    <div className="testrun_value_cards_container">
      {keys.map((key) => (
        <TestrunValueCard key={key} valueKey={key} timeEvent={timeEvent} />
      ))}
    </div>
  );
}
