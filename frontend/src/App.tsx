import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, Menu, Typography, ConfigProvider, theme } from 'antd';
import { DashboardOutlined, GithubOutlined, ApartmentOutlined, CodeOutlined } from '@ant-design/icons';
import { DashboardPage } from './pages/DashboardPage';
import { ReviewDetailPage } from './pages/ReviewDetailPage';
import { RepositoryPage } from './pages/RepositoryPage';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const NavigationMenu: React.FC = () => {
  const location = useLocation();
  
  let selectedKey = 'dashboard';
  if (location.pathname === '/repositories') {
    selectedKey = 'repos';
  } else if (location.pathname.startsWith('/reviews')) {
    selectedKey = 'dashboard';
  }
  
  return (
    <Menu
      theme="dark"
      mode="horizontal"
      selectedKeys={[selectedKey]}
      style={{ flex: 1, justifyContent: 'flex-end', background: 'transparent', borderBottom: 0 }}
      items={[
        {
          key: 'dashboard',
          icon: <DashboardOutlined />,
          label: <Link to="/">Dashboard</Link>,
        },
        {
          key: 'repos',
          icon: <ApartmentOutlined />,
          label: <Link to="/repositories">Repositories</Link>,
        },
        {
          key: 'docs',
          icon: <CodeOutlined />,
          label: <a href="/docs" target="_blank" rel="noreferrer">API Docs</a>,
        },
      ]}
    />
  );
};

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 8,
          colorBgContainer: '#14141d',
          colorBgLayout: '#0d0c12',
        },
      }}
    >
      <BrowserRouter>
        <Layout style={{ minHeight: '100vh' }}>
          <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <Title level={4} style={{ margin: 0, display: 'flex', alignItems: 'center', color: '#fff' }}>
                <GithubOutlined style={{ marginRight: 10, color: '#1890ff', fontSize: '24px' }} />
                <span>CodeReview<span className="gradient-text">.AI</span></span>
              </Title>
            </div>
            <NavigationMenu />
          </Header>
          <Content style={{ padding: '40px 24px', maxWidth: 1200, width: '100%', margin: '0 auto' }}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/reviews/:id" element={<ReviewDetailPage />} />
              <Route path="/repositories" element={<RepositoryPage />} />
            </Routes>
          </Content>
          <Footer style={{ textAlign: 'center', background: 'transparent', color: '#434343' }}>
            AI GitHub Code Review Platform ©2026 Created by Antigravity AI
          </Footer>
        </Layout>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
