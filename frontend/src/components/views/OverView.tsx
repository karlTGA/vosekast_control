import React from "react";
import { Layout } from "antd";
import CommandButtonsBar from "../CommandButtonsBar";

const { Sider, Content } = Layout;

const OverView = () => {
  return (
    <Layout>
      <Sider className="sider-overview">
        <CommandButtonsBar />
      </Sider>
      <Content>Content</Content>
    </Layout>
  );
};

export default OverView;
