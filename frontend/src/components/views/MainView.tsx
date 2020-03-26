import React from "react";
import { Layout } from "antd";

import Routes from "../../Routes";
import NavHeader from "../NavHeader";

const MainView = () => {
  return (
    <Layout>
      <NavHeader />
      <Routes />
    </Layout>
  );
};

export default MainView;
