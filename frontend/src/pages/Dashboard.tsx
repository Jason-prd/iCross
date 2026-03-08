import { useState, useEffect } from "react";
import { Card, Row, Col, Statistic, Table, Tag, Spin } from "antd";
import {
  ShopOutlined,
  ShoppingOutlined,
  InboxOutlined,
  WarningOutlined,
  UserOutlined,
  RiseOutlined,
} from "@ant-design/icons";
import {
  shopsApi,
  productsApi,
  ordersApi,
  inventoryApi,
  customersApi,
} from "../services/api";
import dayjs from "dayjs";

interface RecentOrder {
  id: string;
  order_number: string;
  customer_name?: string;
  total_amount: number;
  status: string;
  created_at: string;
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    shops: 0,
    products: 0,
    pendingOrders: 0,
    lowStockAlerts: 0,
    customers: 0,
    todayOrders: 0,
    todayRevenue: 0,
  });
  const [recentOrders, setRecentOrders] = useState<RecentOrder[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [shopsRes, productsRes, ordersRes, inventoryRes, customersRes] =
        await Promise.all([
          shopsApi.getAll().catch(() => ({ data: [], meta: { total: 0 } })),
          productsApi
            .getAll({ limit: 1 })
            .catch(() => ({ data: [], meta: { total: 0 } })),
          ordersApi
            .getAll({ limit: 5 })
            .catch(() => ({ data: [], meta: { total: 0 } })),
          inventoryApi
            .getAll({ low_stock: true, limit: 1 })
            .catch(() => ({ data: [], meta: { total: 0 } })),
          customersApi
            .getAll()
            .catch(() => ({ data: [], meta: { total: 0 } })),
        ]);

      const orders = ordersRes.data || [];
      const today = dayjs().format("YYYY-MM-DD");
      const todayOrders = orders.filter(
        (o: RecentOrder) => dayjs(o.created_at).format("YYYY-MM-DD") === today,
      );

      setStats({
        shops: Array.isArray(shopsRes.data) ? shopsRes.data.length : 0,
        products: productsRes.meta?.total || 0,
        pendingOrders: orders.filter(
          (o: RecentOrder) =>
            o.status === "pending" || o.status === "confirmed",
        ).length,
        lowStockAlerts: inventoryRes.meta?.total || 0,
        customers: customersRes.meta?.total || 0,
        todayOrders: todayOrders.length,
        todayRevenue: todayOrders.reduce(
          (sum: number, o: RecentOrder) => sum + o.total_amount,
          0,
        ),
      });
      setRecentOrders(orders.slice(0, 5));
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const ORDER_STATUS: Record<string, { label: string; color: string }> = {
    pending: { label: "待处理", color: "orange" },
    confirmed: { label: "已确认", color: "blue" },
    shipped: { label: "已发货", color: "geekblue" },
    delivered: { label: "已完成", color: "green" },
    cancelled: { label: "已取消", color: "red" },
  };

  const orderColumns = [
    {
      title: "订单号",
      dataIndex: "order_number",
      key: "order_number",
      render: (num: string) => (
        <span style={{ fontFamily: "monospace" }}>{num}</span>
      ),
    },
    {
      title: "客户",
      dataIndex: "customer_name",
      key: "customer_name",
      render: (name: string) => name || "-",
    },
    {
      title: "金额",
      dataIndex: "total_amount",
      key: "total_amount",
      render: (v: number) => `¥${v?.toFixed(2) || "0.00"}`,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: (status: string) => {
        const s = ORDER_STATUS[status] || { label: status, color: "default" };
        return <Tag color={s.color}>{s.label}</Tag>;
      },
    },
    {
      title: "时间",
      dataIndex: "created_at",
      key: "created_at",
      render: (time: string) => dayjs(time).format("MM-DD HH:mm"),
    },
  ];

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 400,
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <h1>仪表盘</h1>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="店铺数量"
              value={stats.shops}
              prefix={<ShopOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="商品数量"
              value={stats.products}
              prefix={<ShoppingOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理订单"
              value={stats.pendingOrders}
              prefix={<InboxOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="库存预警"
              value={stats.lowStockAlerts}
              prefix={<WarningOutlined />}
              valueStyle={{
                color: stats.lowStockAlerts > 0 ? "#f5222d" : "#52c41a",
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="客户总数"
              value={stats.customers}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日订单"
              value={stats.todayOrders}
              prefix={<RiseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日销售额"
              value={stats.todayRevenue}
              prefix="¥"
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="系统状态"
              value="正常"
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="最近订单" style={{ marginBottom: 24 }}>
        <Table
          columns={orderColumns}
          dataSource={recentOrders}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
}
