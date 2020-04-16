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
  // @ts-ignore
} from "react-timeseries-charts";

export default function TestrunChart({
  testrun,
}: {
  testrun: TestrunInfos | undefined;
}) {
  if (testrun?.results == null) return <></>;
  const series = testrun.results;
  const style = styler([
    {
      key: "scale_value",
      color: "#a02c2c",
      width: 2,
    },
    {
      key: "flow_value",
      color: "#a02c2c",
      width: 2,
    },
  ]);

  return (
    <Resizable>
      <ChartContainer
        // @ts-ignore
        timeRange={series.range()}
        showGrid={true}
      >
        <ChartRow height="500">
          <YAxis
            id="scale_value"
            label="Scale"
            // @ts-ignore
            min={series.min("scale_value")}
            max={series.max("scale_value")}
            width="60"
            format=".2f"
          />
          <Charts>
            <LineChart
              axis="scale_value"
              series={series}
              columns={["scale_value", "flow_value"]}
              style={style}
            />
          </Charts>
        </ChartRow>
      </ChartContainer>
    </Resizable>
  );
}
