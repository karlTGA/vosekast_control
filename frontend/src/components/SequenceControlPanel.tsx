import React, { useEffect, useState } from "react";
import QueryDataChart from "./QueryDataChart";
import { useStoreState } from "pullstate";
import { VosekastStore } from "../Store";
import MQTTConnection from "../utils/MQTTConnection";
import {  Button } from 'antd';
import {  DownloadOutlined } from '@ant-design/icons';

export default function SequenceControlPanel(){
  const [foundActiveRun, setFoundActiveRun] = useState(false);
  const [inputValue, setNewId] = useState("");
  const [queryId, setQueryId] = useState("");
  
  const changeId = (e) => {
    setNewId(e.target.value);
  };
  
  const getId = () => {
    setNewId("");
    setQueryId(inputValue);
    setFoundActiveRun(false)
  };
 
  const oldRuns = useStoreState(VosekastStore, (s) => s.testruns);
  
  const queryRun = Array.from(oldRuns.values()).find(
    (testrun) => testrun.id === queryId
  );
  
  useEffect(() => {
    console.log(queryRun != null)
    console.log(!foundActiveRun)
    if (queryRun != null && !foundActiveRun) {
      console.log("TEST")
      const requestOldData = async () => {
        MQTTConnection.publishCommand(
          "system",
          "testrun_controller",
          "get_test_results",
          { run_id: queryRun.id}
        );
      };

      setFoundActiveRun(true);
      requestOldData();
    }
  }, [queryRun]);

  
  return(
    <>
    <div className="sequence-buttons-bar">
      
      <input placeholder="Data ID" value={inputValue} onChange={changeId} type="tex"/> 
      <Button 
        onClick={getId}
        >Get Data</Button>
      <Button icon={<DownloadOutlined />}>
        Download
      </Button>
      <div className="vl" />
      
    </div>
    
    <QueryDataChart testrun ={queryRun}/>
    </>    
  );
}