import { Layout, Menu } from "antd";
import { useNavigate, useLocation } from "react-router-dom";
import {
  DashboardOutlined,
  ShopOutlined,
  ShoppingOutlined,
  InboxOutlined,
  DatabaseOutlined,
  TeamOutlined,
  SettingOutlined,
  FileSearchOutlined,
  CloudUploadOutlined,
  SendOutlined,
} from "@ant-design/icons";

const { Sider } = Layout;

const menuItems = [
  { key: "/dashboard", icon: <DashboardOutlined />, label: "仪表盘" },
  { key: "/dashboard/new", icon: <DashboardOutlined />, label: "运营仪表盘" },
  { key: "/shops", icon: <ShopOutlined />, label: "店铺管理" },
  {
    key: "products",
    icon: <ShoppingOutlined />,
    label: "商品管理",
    children: [
      { key: "/products/library", label: "商品库" },
      { key: "/products/selection", icon: <FileSearchOutlined />, label: "选品管理" },
      { key: "/products/ozon", icon: <CloudUploadOutlined />, label: "Ozon商品" },
      { key: "/products/amazon", label: "Amazon" },
      { key: "/products/shopify", label: "Shopify" },
    ],
  },
  {
    key: "orders",
    icon: <InboxOutlined />,
    label: "订单管理",
    children: [
      { key: "/orders", label: "Ozon订单" },
      { key: "/orders/dropship", icon: <SendOutlined />, label: "代发订单" },
    ],
  },
  { key: "/inventory", icon: <DatabaseOutlined />, label: "库存管理" },
  { key: "/customers", icon: <TeamOutlined />, label: "客户管理" },
  {
    key: "settings",
    icon: <SettingOutlined />,
    label: "配置管理",
    children: [
      { key: "/settings/ozon", label: "Ozon配置" },
    ],
  },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const getSelectedKeys = () => {
    const path = location.pathname;
    if (path.startsWith("/products/")) {
      return [path];
    }
    if (path.startsWith("/orders/")) {
      return [path];
    }
    return [path];
  };

  return (
    <Sider theme="light" width={220} style={{ background: "#fff" }}>
      <div style={{ padding: "16px", borderBottom: "1px solid #f0f0f0" }}>
        <h2 style={{ margin: 0, color: "#1890ff" }}>iCross</h2>
        <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#8c8c8c" }}>
          跨境电商运营系统
        </p>
      </div>
      <Menu
        mode="inline"
        selectedKeys={getSelectedKeys()}
        style={{ borderRight: 0 }}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
      />
    </Sider>
  );
}
