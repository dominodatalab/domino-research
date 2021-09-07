import * as React from 'react';
import { Layout, Menu } from 'antd';
const { Content, Header } = Layout;
import { Link } from 'react-router-dom';
import { RollbackOutlined } from '@ant-design/icons';

const OuterLayout: React.FC = ({ children }) => {
  return (
    <Layout style={{ height: '100vh' }}>
      <Header>
        <Menu theme="dark" mode="horizontal" selectable={false}>
          <Menu.Item key="brand">
            <Link to="/checkpoint/requests">🛂 Checkpoint</Link>
          </Menu.Item>
          <Menu.Item key="requests">
            <Link to="/checkpoint/requests">Promote Requests</Link>
          </Menu.Item>
          <Menu.Item key="mlflow" icon={<RollbackOutlined />} style={{ marginLeft: 'auto' }}>
            <a href="/">Back to Registry</a>
          </Menu.Item>
        </Menu>
      </Header>
      <Content>{children}</Content>
    </Layout>
  );
};

export default OuterLayout;
