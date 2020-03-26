import React from "react";
import "./App.scss";
import {
  MQTTOnlineIndicator,
  VosekastOnlineIndicator,
  ErrorIndicator
} from "./components/Indicators";
import { ScaleTag } from "./components/Scale";
import { PumpTag } from "./components/Pump";
import MainView from "./components/views/MainView";
import { BrowserRouter as Router } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <Router>
        <MainView />
      </Router>
      {/* <MQTTOnlineIndicator />
      <VosekastOnlineIndicator />
      <ErrorIndicator />
      <ScaleTag />
      <PumpTag pumpId="pump_measuring_tank" /> */}
    </div>
  );
}

export default App;
