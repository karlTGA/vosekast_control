/// <reference types="react-scripts" />

declare module "react-timeseries-charts" {
  import React from "react";
  import { TimeRange } from "pondjs";

  type Style = Any;

  interface StyleObject {
    key: string;
    color: string;
    width: number;
  }
  export function styler(styles: Array<StyleObject>): Style;

  // Chart Container
  export interface ChartContainerProps {
    timeRange?: TimeRange;
    showGrid?: boolean;
    format?: string;
    children: React.ReactNode;
  }

  export const ChartContainer: (
    props: ChartContainerProps
  ) => React.ReactElement<ChartContainerProps>;

  // Chart Row
  export interface ChartRowProps {
    height?: string;
    weight?: string;
    children: React.ReactNode;
  }

  export const ChartRow: (
    props: ChartRowProps
  ) => React.ReactElement<ChartRowProps>;

  // Y Axis
  export interface YAxisProps {
    id?: string;
    label?: string;
    min?: number;
    max?: number;
    width?: string;
    format?: string;
    showGrid?: boolean;
  }

  export const YAxis: (props: YAxisProps) => React.ReactElement<YAxisProps>;

  // Charts
  export interface ChartsProps {
    children: React.ReactNode;
  }

  export const Charts: (props: ChartsProps) => React.ReactElement<ChartsProps>;

  // LineChart
  export interface LineChartProps {
    axis?: string;
    series: TimeSeries;
    columns: Array<string>;
    style: Style;
  }

  export const LineChart: (
    props: LineChartProps
  ) => React.ReactElement<LineChartProps>;

  // Resizable
  export interface ResizableProps {
    children: React.ReactNode;
  }

  export const Resizable: (
    props: ResizableProps
  ) => React.ReactElement<ResizableProps>;
}

declare module "pondjs" {
  interface TimeSerieData {
    name: string;
    columns: Array<string>;
    points: Array<Array<number>>;
  }

  export type TimeRange = Any;

  export declare class Event {
    constructor(timestamp: number, value: Record<string, number>);
    get(arg0: string): number;
  }

  export declare class Collection {
    constructor();

    addEvent(event: TimeEvent);
  }

  export declare class TimeSeries {
    constructor(timeSerieData: TimeSerieData);

    collection(): Collection;
    setCollection(collection: Collection, arg1: boolean);
    range(): TimeRange;
    min(serie: string): number;
    max(serie: string): number;
    atLast(): Event;
  }

  export declare class TimeEvent {
    constructor(time: number, values: Record<string, number>);
  }
}
