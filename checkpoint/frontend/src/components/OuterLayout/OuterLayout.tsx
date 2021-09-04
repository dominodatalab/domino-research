import * as React from 'react';
import { Layout, Menu } from 'antd';
const { Content, Header } = Layout;
import { Link } from 'react-router-dom';

const OuterLayout: React.FC = ({ children }) => {
  return (
    <Layout style={{ height: '100vh' }}>
      <Header>
        <Menu theme="dark" mode="horizontal">
          <Menu.Item>
            <a href="/">Back to Mlflow</a>
          </Menu.Item>
          <Menu.Item>
            <Link to="/checkpoint/requests">Promote Requests</Link>
          </Menu.Item>
        </Menu>
      </Header>
      <Content>{children}</Content>
    </Layout>
  );
};

export default OuterLayout;
