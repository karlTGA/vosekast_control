import React from "react";
import { VosekastStore } from "../Store";
import { useStoreState } from "pullstate";
import MQTTConnection from "../utils/MQTTConnection";
// @ts-ignore
import useInterval from "react-useinterval";

const SequencesList = () => {
  const runIds = useStoreState(VosekastStore, (s) => s.testruns);
  useInterval(
    () => MQTTConnection.publishCommand("system", "db", "get_run_ids"),
    5000
  );

  if (runIds == null) return <></>;

  return (
    <div className="sequences-list">
      {Array.from(runIds).map(([runId, runInfos]) => (
        <div className="sequenses-entry">{runId}</div>
      ))}
    </div>
  );
};

export default SequencesList;
