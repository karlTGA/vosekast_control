import React from "react";
import { Layout } from "antd";
import DeviceButtonsBar from "../DeviceButtonsBar";
import SequenceControlPanel from "../SequenceControlPanel";

const { Sider, Content } = Layout;

const OverView = () => {
  return (
    <Layout>
      <Sider className="sider-overview">
        <DeviceButtonsBar />
      </Sider>
      <Content className="content-overview">
        <SequenceControlPanel />
      </Content>
    </Layout>
  );
};

export default OverView;
