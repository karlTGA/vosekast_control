import React from "react";
import "./App.css";
import {
  MQTTOnlineIndicator,
  VosekastOnlineIndicator,
  ErrorIndicator
} from "./components/Indicators";
import { ScaleTag } from "./components/Scale";

function App() {
  return (
    <div className="App">
      <MQTTOnlineIndicator />
      <VosekastOnlineIndicator />
      <ErrorIndicator />
      <ScaleTag />
    </div>
  );
}

export default App;
