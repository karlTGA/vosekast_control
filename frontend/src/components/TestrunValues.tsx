import React from "react";
import { TestrunInfos } from "../Store";
import { Event } from "pondjs";
import { Card } from "antd";

interface ValueProps {
  title: string;
  imagePath: string;
}

const valueMapping: Record<string, ValueProps> = {
  scale_value: {
    title: "Scale in kg",
    imagePath: "/img/icons/manufacturing/025-meter.svg",
  },
  flow_value: {
    title: "Flow in l/min",
    imagePath: "/img/icons/manufacturing/020-planning.svg",
  },
};

function TestrunValueCard({
  valueKey,
  timeEvent,
}: {
  valueKey: string;
  timeEvent: Event;
}) {
  const valueProps = valueMapping[valueKey];
  const value = Math.round(timeEvent.get(valueKey) * 1000) / 1000;

  return (
    <Card className="testrun_value_card">
      <div className="testrun_value_card_icon">
        <img src={valueProps.imagePath} />
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
  const timeEvent = testrun.results.atLast() as Event;

  return (
    <div className="testrun_value_cards_container">
      {keys.map((key) => {
        debugger;
        return <TestrunValueCard valueKey={key} timeEvent={timeEvent} />;
      })}
    </div>
  );
}
