import React from "react";
import TestrunButtonsBar from "./TestrunButtonsBar";
import TestrunChart from "./TestrunChart";
import TestrunValues from "./TestrunValues";
import { useStoreState } from "pullstate";
import { VosekastStore } from "../Store";

export default function TestrunControlPanel() {
  const testruns = useStoreState(VosekastStore, (s) => s.testruns);
  const activeRun = Array.from(testruns.values()).find(
    (testrun) => testrun.state === "MEASURING"
  );

  return (
    <>
      <TestrunButtonsBar testrun={activeRun} />
      <TestrunChart testrun={activeRun} />
      <TestrunValues testrun={activeRun} />
    </>
  );
}
