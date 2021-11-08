import React from "react";
import { Layout } from "antd";
import SequencesList from "../SequencesList";
import SequenceControlPanel from "../SequenceControlPanel";
const { Sider, Content } = Layout;

const SequencesView = () => {
  return (
    <Layout>
      <Sider className="sider-overview">
        <SequencesList />
      </Sider>
      <Content className="content-overview">
        <SequenceControlPanel />
      </Content>
    </Layout>
  );
};

export default SequencesView;
