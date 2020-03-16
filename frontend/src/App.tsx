import React from "react";
import "./App.css";
import {
  MQTTOnlineIndicator,
  VosekastOnlineIndicator,
  ErrorIndicator
} from "./components/Indicators";
import { ScaleTag } from "./components/Scale";
import { PumpTag } from "./components/Pump";

function App() {
  return (
    <div className="App">
      <MQTTOnlineIndicator />
      <VosekastOnlineIndicator />
      <ErrorIndicator />
      <ScaleTag />
      <PumpTag pumpId="pump_measuring_tank" />
    </div>
  );
}

export default App;
