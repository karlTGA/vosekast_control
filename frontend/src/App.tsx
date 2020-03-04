import React from "react";
import "./App.css";
import { OnlineIndicator, ErrorIndicator } from "./components/Indicators";

function App() {
  return (
    <div className="App">
      <OnlineIndicator />
      <ErrorIndicator />
    </div>
  );
}

export default App;
