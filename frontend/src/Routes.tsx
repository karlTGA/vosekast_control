import React from "react";
import { Switch, Route } from "react-router-dom";
import { Layout } from "antd";

import OverView from "./components/views/OverView";
import SequencesView from "./components/views/SequencesView";

export default function Routes() {
  return (
    <Layout>
      <Switch>
        <Route path="/" exact component={OverView} />
        <Route path="/sequences" component={SequencesView} />
      </Switch>
    </Layout>
  );
}
