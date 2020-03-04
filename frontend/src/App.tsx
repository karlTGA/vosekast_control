import React from "react";
import "./App.css";
import { OnlineIndicator, ErrorIndicator } from "./components/Indicators";
import { ScaleTag } from "./components/Scale";

function App() {
  return (
    <div className="App">
      <OnlineIndicator />
      <ErrorIndicator />
      <ScaleTag />
    </div>
  );
}

export default App;
