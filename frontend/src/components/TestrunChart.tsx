import React from "react";
import { TestrunInfos } from "../Store";
import {
  ChartContainer,
  ChartRow,
  YAxis,
  Charts,
  LineChart,
  Resizable,
  styler,
} from "react-timeseries-charts";
import { Card } from "antd";

export default function TestrunChart({
  testrun,
}: {
  testrun: TestrunInfos | undefined;
}) {
  if (testrun?.results == null) return <></>;
  const series = testrun.results;
  const style = styler([
    {
      key: "scaleValue",
      color: "red",
      width: 2,
    },
    {
      key: "flowValue",
      color: "blue",
      width: 2,
    },
  ]);

  return (
    <Card title="Results" className="testrun_chart">
      <Resizable>
        <ChartContainer
          timeRange={series.range()}
          showGrid={true}
          format="%H:%m:%S"
        >
          <ChartRow height="500">
            <YAxis
              id="scaleValue"
              label="Scale Value in kg"
              min={series.min("scaleValue")}
              max={series.max("scaleValue")}
              width="60"
              format=".2f"
              showGrid
            />
            <Charts>
              <LineChart
                axis="scaleValue"
                series={series}
                columns={["scaleValue", "flowValue"]}
                style={style}
              />
            </Charts>
          </ChartRow>
        </ChartContainer>
      </Resizable>
    </Card>
  );
}
