import React from "react";
import { Switch, Route } from "react-router-dom";
import { Layout } from "antd";

import HomeView from "./components/views/HomeView";

export default function Routes() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={HomeView} />
      </Switch>
    </Layout>
  );
}
