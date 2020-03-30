import React from "react";
import { Layout } from "antd";

import Routes from "../../Routes";
import NavHeader from "../NavHeader";
import Footer from "../Footer";

const MainView = () => {
  return (
    <Layout>
      <NavHeader />
      <Routes />
      <Footer />
    </Layout>
  );
};

export default MainView;
