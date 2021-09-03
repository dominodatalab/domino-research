import * as React from 'react';
import { useState } from 'react';
import { Layout, Menu } from 'antd';
import { Breadcrumb } from '@domino-research/ui';
const { Content, Sider } = Layout;
const { SubMenu } = Menu;

const handleMenuClick = (e: any) => console.log('Clicked on: ', e.key);
import { DesktopOutlined, PieChartOutlined, FileOutlined, UserOutlined } from '@ant-design/icons';

const OuterLayout: React.FC = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const handleCollapse = () => setCollapsed(!collapsed);
  return (
    <div>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider collapsible collapsed={collapsed} onCollapse={handleCollapse}>
          <div className="logo" />
          <Menu theme="dark" mode="inline" onClick={handleMenuClick}>
            <Menu.Item key="1" icon={<PieChartOutlined />}>
              Option 1
            </Menu.Item>
            <Menu.Item key="2" icon={<DesktopOutlined />}>
              Option 2
            </Menu.Item>
            <SubMenu key="sub1" icon={<UserOutlined />} title="User">
              <Menu.Item key="3">Tom</Menu.Item>
              <Menu.Item key="4">Bill</Menu.Item>
              <Menu.Item key="5">Alex</Menu.Item>
            </SubMenu>
            <Menu.Item key="9" icon={<FileOutlined />}>
              Files
            </Menu.Item>
          </Menu>
        </Sider>
        <Layout className="site-layout">
          <Content style={{ margin: '0' }}>
            <Breadcrumb breadcrumb={[{ title: 'projects' }]} />
            <div className="site-layout-background" style={{ padding: 24, minHeight: 360 }}>
              {children}
            </div>
          </Content>
        </Layout>
      </Layout>
    </div>
  );
};

export default OuterLayout;
