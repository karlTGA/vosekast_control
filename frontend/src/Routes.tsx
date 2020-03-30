import React from "react";
import { Switch, Route } from "react-router-dom";
import { Layout } from "antd";

import OverView from "./components/views/OverView";

export default function Routes() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={OverView} />
      </Switch>
    </Layout>
  );
}
