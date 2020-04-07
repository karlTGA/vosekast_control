import React from "react";
import { Layout } from "antd";
import DeviceButtonsBar from "../DeviceButtonsBar";
import TestrunControlPanel from "../TestrunControlPanel";

const { Sider, Content } = Layout;

const OverView = () => {
  return (
    <Layout>
      <Sider className="sider-overview">
        <DeviceButtonsBar />
      </Sider>
      <Content className="content-overview">
        <TestrunControlPanel />
      </Content>
    </Layout>
  );
};

export default OverView;
