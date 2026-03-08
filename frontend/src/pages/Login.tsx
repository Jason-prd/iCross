import { useState } from "react";
import { Form, Input, Button, Card, message } from "antd";
import {
  UserOutlined,
  LockOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "../stores/auth";
import { authApi } from "../services/api";

const isDev = import.meta.env.DEV;

const TEST_ACCOUNTS = [
  { email: "admin@icross.com", password: "admin123" },
  { email: "test@icross.com", password: "test123" },
];

export default function Login() {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const { login } = useAuthStore();

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const response = await authApi.login(values.email, values.password);
      const { access_token, user } = response;
      login(user, access_token);
      message.success("登录成功");
      window.location.href = "/dashboard";
    } catch (error: any) {
      console.error("Login error:", error);
      message.error(error.response?.data?.detail || error.message || "登录失败");
    } finally {
      setLoading(false);
    }
  };

  const handleDevFill = (account: (typeof TEST_ACCOUNTS)[0]) => {
    form.setFieldsValue(account);
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background: "#f5f5f5",
      }}
    >
      <Card style={{ width: 400 }}>
        <h2 style={{ textAlign: "center", marginBottom: 24 }}>iCross 登录</h2>
        <Form form={form} name="login" onFinish={onFinish} size="large">
          <Form.Item
            name="email"
            rules={[{ required: true, message: "请输入邮箱" }]}
          >
            <Input prefix={<UserOutlined />} placeholder="邮箱" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: "请输入密码" }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登录
            </Button>
          </Form.Item>
        </Form>
        {isDev && (
          <div
            style={{
              marginTop: 16,
              paddingTop: 16,
              borderTop: "1px solid #f0f0f0",
            }}
          >
            <div style={{ fontSize: 12, color: "#999", marginBottom: 8 }}>
              开发环境 - 一键填充
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {TEST_ACCOUNTS.map((account) => (
                <Button
                  key={account.email}
                  icon={<ThunderboltOutlined />}
                  onClick={() => handleDevFill(account)}
                  size="small"
                >
                  {account.email.split("@")[0]}
                </Button>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
