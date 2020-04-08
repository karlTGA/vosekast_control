import React, { useEffect } from "react";
import TestrunButtonsBar from "./TestrunButtonsBar";
import TestrunChart from "./TestrunChart";
import MQTTConnection from "../utils/MQTTConnection";
import { useStoreState } from "pullstate";
import { VosekastStore } from "../Store";

export default function TestrunControlPanel() {
  const testruns = useStoreState(VosekastStore, (s) => s.testruns);
  const activeRun = Array.from(testruns.values()).find(
    (testrun) => testrun.state === "MEASURING"
  );
  useEffect(() => {
    MQTTConnection.publishCommand(
      "system",
      "testrun_controller",
      "get_current_run_infos"
    );
  }, []);

  return (
    <>
      <TestrunButtonsBar testrun={activeRun} />
      <TestrunChart testrun={activeRun} />
    </>
  );
}
