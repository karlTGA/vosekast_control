import React, { useEffect, useState } from "react";
import QueryDataChart from "./QueryDataChart";
import { useStoreState } from "pullstate";
import { VosekastStore } from "../Store";
import MQTTConnection from "../utils/MQTTConnection";
import {  Button } from 'antd';
import { CSVLink } from "react-csv"

export default function SequenceControlPanel(){
  const [foundActiveRun, setFoundActiveRun] = useState(false);
  const [inputValue, setNewId] = useState("");
  const [queryId, setQueryId] = useState("");
  const [csvData, setCsvData] = useState([{}]);
  const [bolleanDownload, setBolleanDownload] = useState(true)
  
  const changeId = (e) => {
    setNewId(e.target.value);
  };
  
  const getId = () => {
    setNewId("");
    setQueryId(inputValue);
    setFoundActiveRun(false);
  };
  const oldRuns = useStoreState(VosekastStore, (s) => s.testruns);
  
  const queryRun = Array.from(oldRuns.values()).find(
    (testrun) => testrun.id === queryId
  );
  
  useEffect(() => {
    if (queryRun?.results != null) {
      setCsvData(queryRun.results.toJSON().points)
      setBolleanDownload(false)
    };

    if (queryRun != null && !foundActiveRun) {
      
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
      
          };
     
  }, [queryRun]);
  
  const disableDownload = () => {
    setBolleanDownload(true)
  };
   
  return(
    <>
    <div className="sequence-buttons-bar">
      
      <input placeholder="Data ID" value={inputValue} onChange={changeId} type="tex"/> 
      <Button 
        onClick={getId}
        >Get Data</Button>
      <Button  disabled={bolleanDownload} onClick={disableDownload}>
        <CSVLink
          data={csvData} 
          separator={";"}
          headers = {[
            "time", "messaure", "flow" ]
            } 
          filename={"Download"}
          className="btn btn-primary"
          target="_blank"                
        >
        Download 
        </CSVLink>
      </Button>
      
      <div className="vl" />
      
    </div>
    
    <QueryDataChart testrun ={queryRun}/>
    </>    
  );
}