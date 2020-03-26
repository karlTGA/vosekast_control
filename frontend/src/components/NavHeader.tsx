import React from "react";
import { Layout, Menu } from "antd";
import { Link } from "react-router-dom";

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
      </Menu>
    </Header>
  );
}
