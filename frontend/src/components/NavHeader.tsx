import React from "react";
import { Layout, Menu, Tag } from "antd";
import { Link } from "react-router-dom";
import { MQTTOnlineIndicator, VosekastOnlineIndicator } from "./Indicators";
import VosekastStateTag from "./VosekastStateTag";

const { Header } = Layout;

export default function NavHeader() {
  return (
    <Header className="header">
      <Link to="/">
        <div className="logo" />
      </Link>

      <Menu theme="dark" mode="horizontal">
        <Menu.Item key="overview">
          <Link to="/">Overview</Link>
        </Menu.Item>
        <Menu.Item key="sequences">
          <Link to="/sequences">Test Sequences</Link>
        </Menu.Item>
        <Menu.Item
          key="mqtt_indicator"
          className="indicator-menu-item"
          disabled
        >
          <MQTTOnlineIndicator />
        </Menu.Item>
        <Menu.Item
          key="vosekast_indicator"
          className="indicator-menu-item"
          disabled
        >
          <VosekastOnlineIndicator />
        </Menu.Item>
        <Menu.Item key="vosekast_state" className="state-menu-item" disabled>
          <VosekastStateTag />
        </Menu.Item>
      </Menu>
    </Header>
  );
}
