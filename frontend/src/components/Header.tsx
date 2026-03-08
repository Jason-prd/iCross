import { Layout, Dropdown, Avatar, Typography } from "antd";
import {
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  BellOutlined,
  GlobalOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "../stores/auth";

const { Header: AntHeader } = Layout;
const { Text } = Typography;

export default function Header() {
  const { user, logout } = useAuthStore();

  const userMenuItems = [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: "个人资料",
    },
    {
      key: "settings",
      icon: <SettingOutlined />,
      label: "系统设置",
    },
    {
      type: "divider" as const,
    },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "退出登录",
      onClick: logout,
    },
  ];

  return (
    <AntHeader
      style={{
        background: "#fff",
        borderBottom: "1px solid #f0f0f0",
        padding: "0 16px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        height: "48px",
      }}
    >
      {/* Left side - Global controls */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <GlobalOutlined style={{ fontSize: "14px", color: "#8c8c8c" }} />
          <Text type="secondary" style={{ fontSize: "12px" }}>
            全球配置
          </Text>
        </div>
        <div
          style={{
            height: "16px",
            width: "1px",
            background: "#f0f0f0",
          }}
        />
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <BellOutlined style={{ fontSize: "14px", color: "#8c8c8c" }} />
          <Text type="secondary" style={{ fontSize: "12px" }}>
            通知
          </Text>
        </div>
      </div>

      {/* Right side - User info */}
      <Dropdown menu={{ items: userMenuItems }} trigger={["click"]}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            cursor: "pointer",
            padding: "4px 8px",
            borderRadius: "4px",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "#f5f5f5")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "")}
        >
          <Avatar
            size="small"
            icon={<UserOutlined />}
            style={{ background: "#1890ff" }}
          />
          <div style={{ display: "flex", flexDirection: "column" }}>
            <Text strong style={{ fontSize: "12px", lineHeight: "1.2" }}>
              {user?.name || "用户"}
            </Text>
            <Text
              type="secondary"
              style={{ fontSize: "10px", lineHeight: "1.2" }}
            >
              {user?.email || ""}
            </Text>
          </div>
        </div>
      </Dropdown>
    </AntHeader>
  );
}
