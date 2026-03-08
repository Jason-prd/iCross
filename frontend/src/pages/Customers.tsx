import { useState, useEffect } from "react";
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Descriptions,
  Timeline,
  Form,
  Input,
  Select,
  message,
  Pagination,
} from "antd";
import {
  SearchOutlined,
  EyeOutlined,
  MessageOutlined,
} from "@ant-design/icons";
import { customersApi } from "../services/api";
import dayjs from "dayjs";

interface Customer {
  id: string;
  name?: string;
  email?: string;
  phone?: string;
  company?: string;
  customer_type: string;
  level: string;
  tags: string[];
  total_orders: number;
  total_spent: number;
  last_order_date?: string;
  created_at: string;
}

interface Communication {
  id: string;
  type: string;
  direction: string;
  subject?: string;
  content: string;
  status: string;
  follow_up_action?: string;
  follow_up_date?: string;
  created_at: string;
}

const CUSTOMER_LEVELS: Record<string, { label: string; color: string }> = {
  normal: { label: "普通", color: "default" },
  silver: { label: "银卡", color: "#a0a0a0" },
  gold: { label: "金卡", color: "gold" },
  platinum: { label: "白金", color: "#13c2c2" },
  vip: { label: "VIP", color: "#f50" },
};

const COMMUNICATION_TYPES: Record<string, string> = {
  email: "邮件",
  phone: "电话",
  chat: "在线聊天",
  wechat: "微信",
  note: "备注",
};

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [commModalOpen, setCommModalOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(
    null,
  );
  const [communications, setCommunications] = useState<Communication[]>([]);
  const [searchText, setSearchText] = useState("");
  const [levelFilter, setLevelFilter] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [commForm] = Form.useForm();

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const res = await customersApi.getAll({
        page,
        limit: pageSize,
        q: searchText || undefined,
        level: levelFilter,
      });
      setCustomers(res.data.data);
      setTotal(res.data.meta.total);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "获取客户列表失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [page, pageSize, levelFilter]);

  const handleSearch = () => {
    setPage(1);
    fetchCustomers();
  };

  const handleViewDetail = async (customer: Customer) => {
    try {
      const res = await customersApi.getOne(customer.id);
      setSelectedCustomer(res.data);
      setDetailModalOpen(true);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "获取客户详情失败");
    }
  };

  const handleViewCommunications = async (customer: Customer) => {
    try {
      setSelectedCustomer(customer);
      const res = await customersApi.getCommunications(customer.id);
      setCommunications(res.data.data || []);
      commForm.resetFields();
      setCommModalOpen(true);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "获取沟通记录失败");
    }
  };

  const handleAddCommunication = async (values: any) => {
    if (!selectedCustomer) return;
    try {
      await customersApi.addCommunication(selectedCustomer.id, values);
      message.success("沟通记录已添加");
      const res = await customersApi.getCommunications(selectedCustomer.id);
      setCommunications(res.data.data || []);
      commForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "添加沟通记录失败");
    }
  };

  const columns = [
    {
      title: "客户",
      key: "customer",
      render: (_: any, record: Customer) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 500 }}>{record.name || "未命名"}</span>
          <span style={{ color: "#999", fontSize: 12 }}>
            {record.email || record.phone || ""}
          </span>
        </Space>
      ),
    },
    {
      title: "公司",
      dataIndex: "company",
      key: "company",
      render: (company: string) => company || "-",
    },
    {
      title: "等级",
      dataIndex: "level",
      key: "level",
      render: (level: string) => {
        const l = CUSTOMER_LEVELS[level] || CUSTOMER_LEVELS.normal;
        return <Tag color={l.color}>{l.label}</Tag>;
      },
    },
    {
      title: "类型",
      dataIndex: "customer_type",
      key: "customer_type",
      render: (type: string) => (type === "wholesale" ? "批发" : "零售"),
    },
    {
      title: "订单数",
      dataIndex: "total_orders",
      key: "total_orders",
      render: (count: number) => count,
    },
    {
      title: "消费总额",
      dataIndex: "total_spent",
      key: "total_spent",
      render: (spent: number) => `¥${spent.toFixed(2)}`,
    },
    {
      title: "最后下单",
      dataIndex: "last_order_date",
      key: "last_order_date",
      render: (date: string) => (date ? dayjs(date).format("YYYY-MM-DD") : "-"),
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: Customer) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          <Button
            size="small"
            icon={<MessageOutlined />}
            onClick={() => handleViewCommunications(record)}
          >
            沟通
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <h1 style={{ margin: 0 }}>客户管理</h1>
      </div>

      <Space style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索客户姓名、邮箱或电话..."
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          onSearch={handleSearch}
          enterButton
        />
        <Select
          placeholder="客户等级"
          style={{ width: 120 }}
          value={levelFilter}
          onChange={(v) => {
            setLevelFilter(v);
            setPage(1);
          }}
          allowClear
          options={Object.entries(CUSTOMER_LEVELS).map(
            ([value, { label }]) => ({ value, label }),
          )}
        />
      </Space>

      <Table
        columns={columns}
        dataSource={customers}
        rowKey="id"
        loading={loading}
        pagination={false}
      />

      <div style={{ marginTop: 16, textAlign: "right" }}>
        <Pagination
          current={page}
          pageSize={pageSize}
          total={total}
          showSizeChanger
          showTotal={(total) => `共 ${total} 条`}
          onChange={(p, ps) => {
            setPage(p);
            setPageSize(ps);
          }}
        />
      </div>

      <Modal
        title="客户详情"
        open={detailModalOpen}
        onCancel={() => setDetailModalOpen(false)}
        footer={null}
        width={600}
      >
        {selectedCustomer && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="姓名">
              {selectedCustomer.name || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="公司">
              {selectedCustomer.company || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="邮箱">
              {selectedCustomer.email || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="电话">
              {selectedCustomer.phone || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="客户类型">
              {selectedCustomer.customer_type === "wholesale" ? "批发" : "零售"}
            </Descriptions.Item>
            <Descriptions.Item label="客户等级">
              <Tag
                color={
                  CUSTOMER_LEVELS[selectedCustomer.level]?.color || "default"
                }
              >
                {CUSTOMER_LEVELS[selectedCustomer.level]?.label ||
                  selectedCustomer.level}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="订单数">
              {selectedCustomer.total_orders}
            </Descriptions.Item>
            <Descriptions.Item label="消费总额">
              ¥{selectedCustomer.total_spent.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="最后下单">
              {selectedCustomer.last_order_date
                ? dayjs(selectedCustomer.last_order_date).format(
                    "YYYY-MM-DD HH:mm",
                  )
                : "-"}
            </Descriptions.Item>
            <Descriptions.Item label="注册时间">
              {dayjs(selectedCustomer.created_at).format("YYYY-MM-DD")}
            </Descriptions.Item>
            {selectedCustomer.tags.length > 0 && (
              <Descriptions.Item label="标签" span={2}>
                <Space wrap>
                  {selectedCustomer.tags.map((tag, idx) => (
                    <Tag key={idx}>{tag}</Tag>
                  ))}
                </Space>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>

      <Modal
        title={`沟通记录 - ${selectedCustomer?.name || selectedCustomer?.email || ""}`}
        open={commModalOpen}
        onCancel={() => setCommModalOpen(false)}
        footer={null}
        width={700}
      >
        <div style={{ marginBottom: 16 }}>
          <h4>添加沟通记录</h4>
          <Form
            form={commForm}
            layout="inline"
            onFinish={handleAddCommunication}
          >
            <Form.Item
              name="type"
              rules={[{ required: true }]}
              style={{ width: 100 }}
            >
              <Select
                placeholder="类型"
                options={Object.entries(COMMUNICATION_TYPES).map(([v, l]) => ({
                  value: v,
                  label: l,
                }))}
              />
            </Form.Item>
            <Form.Item
              name="direction"
              rules={[{ required: true }]}
              style={{ width: 100 }}
            >
              <Select
                placeholder="方向"
                options={[
                  { value: "outbound", label: "发出" },
                  { value: "inbound", label: "接收" },
                ]}
              />
            </Form.Item>
            <Form.Item
              name="content"
              rules={[{ required: true }]}
              style={{ flex: 1, minWidth: 200 }}
            >
              <Input placeholder="沟通内容" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">
                添加
              </Button>
            </Form.Item>
          </Form>
        </div>

        <div>
          <h4>历史记录</h4>
          {communications.length > 0 ? (
            <Timeline
              items={communications.map((c) => ({
                color: c.direction === "outbound" ? "blue" : "green",
                children: (
                  <div>
                    <div style={{ marginBottom: 4 }}>
                      <Tag>{COMMUNICATION_TYPES[c.type] || c.type}</Tag>
                      <Tag
                        color={c.direction === "outbound" ? "blue" : "green"}
                      >
                        {c.direction === "outbound" ? "发出" : "接收"}
                      </Tag>
                      <span
                        style={{ color: "#999", fontSize: 12, marginLeft: 8 }}
                      >
                        {dayjs(c.created_at).format("YYYY-MM-DD HH:mm")}
                      </span>
                    </div>
                    <div>{c.content}</div>
                    {c.follow_up_action && (
                      <div style={{ color: "#faad14", marginTop: 4 }}>
                        跟进: {c.follow_up_action}
                      </div>
                    )}
                  </div>
                ),
              }))}
            />
          ) : (
            <div style={{ color: "#999", textAlign: "center", padding: 20 }}>
              暂无沟通记录
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}
