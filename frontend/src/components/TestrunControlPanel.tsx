import React, { useEffect, useState } from "react";
import TestrunButtonsBar from "./TestrunButtonsBar";
import TestrunChart from "./TestrunChart";
import TestrunValues from "./TestrunValues";
import { useStoreState } from "pullstate";
import { VosekastStore } from "../Store";
import MQTTConnection from "../utils/MQTTConnection";

export default function TestrunControlPanel() {
  const testruns = useStoreState(VosekastStore, (s) => s.testruns);
  const activeRun = Array.from(testruns.values()).find(
    (testrun) => testrun.state === "MEASURING"
  );
  const [foundActiveRun, setFoundActiveRun] = useState(false);

  useEffect(() => {
    if (activeRun != null && !foundActiveRun) {
      const requestOldData = async () => {
        MQTTConnection.publishCommand(
          "system",
          "testrun_controller",
          "get_test_results",
          { run_id: activeRun.id }
        );
      };

      setFoundActiveRun(true);
      requestOldData();
    }
  }, [activeRun]);

  return (
    <>
      <TestrunButtonsBar testrun={activeRun} />
      <TestrunChart testrun={activeRun} />
      <TestrunValues testrun={activeRun} />
    </>
  );
}
