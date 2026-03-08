import { useState, useEffect } from "react";
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
} from "antd";
import {
  PlusOutlined,
  SyncOutlined,
  EditOutlined,
  DeleteOutlined,
  ShopOutlined,
} from "@ant-design/icons";
import { shopsApi } from "../services/api";

interface Shop {
  id: string;
  name: string;
  platform: string;
  platform_shop_id?: string;
  platform_shop_name?: string;
  status: string;
  last_sync_time?: string;
  last_sync_status?: string;
  api_quota_used: number;
  api_quota_limit?: number;
  created_at: string;
}

const PLATFORMS = [
  { value: "ozon", label: "Ozon" },
  { value: "amazon", label: "Amazon" },
  { value: "shopify", label: "Shopify" },
  { value: "aliexpress", label: "AliExpress" },
  { value: "wildberries", label: "Wildberries" },
];

export default function Shops() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingShop, setEditingShop] = useState<Shop | null>(null);
  const [syncingShopId, setSyncingShopId] = useState<string | null>(null);
  const [form] = Form.useForm();

  const fetchShops = async () => {
    setLoading(true);
    try {
      const res = await shopsApi.getAll();
      setShops(res.data || res);
    } catch (error: any) {
      message.error(error.message || "获取店铺列表失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShops();
  }, []);

  const handleCreate = () => {
    setEditingShop(null);
    form.resetFields();
    form.setFieldsValue({
      platform: "ozon",
      api_credentials: {},
    });
    setModalOpen(true);
  };

  const handleEdit = (shop: Shop) => {
    setEditingShop(shop);
    form.setFieldsValue({
      name: shop.name,
      platform: shop.platform,
    });
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await shopsApi.delete(id);
      message.success("店铺已删除");
      fetchShops();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "删除失败");
    }
  };

  const handleSync = async (id: string) => {
    setSyncingShopId(id);
    try {
      const res = await shopsApi.sync(id);
      message.success(res.data.message || "同步任务已加入队列");
      fetchShops();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "同步失败");
    } finally {
      setSyncingShopId(null);
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingShop) {
        await shopsApi.update(editingShop.id, {
          name: values.name,
          status: values.status,
        });
        message.success("店铺已更新");
      } else {
        await shopsApi.create({
          name: values.name,
          platform: values.platform,
          api_credentials: values.api_credentials || {},
        });
        message.success("店铺已创建");
      }
      setModalOpen(false);
      fetchShops();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "操作失败");
    }
  };

  const columns = [
    {
      title: "店铺名称",
      dataIndex: "name",
      key: "name",
      render: (name: string) => (
        <Space>
          <ShopOutlined />
          {name}
        </Space>
      ),
    },
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      render: (platform: string) => {
        const p = PLATFORMS.find((item) => item.value === platform);
        return <Tag color="blue">{p?.label || platform}</Tag>;
      },
    },
    {
      title: "平台店铺",
      dataIndex: "platform_shop_name",
      key: "platform_shop_name",
      render: (name: string) => name || "-",
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag color={status === "active" ? "green" : "red"}>
          {status === "active" ? "正常" : "停用"}
        </Tag>
      ),
    },
    {
      title: "上次同步",
      dataIndex: "last_sync_time",
      key: "last_sync_time",
      render: (time: string, record: Shop) => (
        <Space direction="vertical" size={0}>
          <span>
            {time ? new Date(time).toLocaleString("zh-CN") : "从未同步"}
          </span>
          {record.last_sync_status && (
            <Tag
              color={record.last_sync_status === "success" ? "green" : "orange"}
            >
              {record.last_sync_status}
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: "API配额",
      key: "api_quota",
      render: (_: any, record: Shop) => (
        <span>
          {record.api_quota_used} / {record.api_quota_limit || "∞"}
        </span>
      ),
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: Shop) => (
        <Space>
          <Button
            size="small"
            icon={<SyncOutlined spin={syncingShopId === record.id} />}
            onClick={() => handleSync(record.id)}
            loading={syncingShopId === record.id}
          >
            同步
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此店铺吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
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
        <h1 style={{ margin: 0 }}>店铺管理</h1>
        <Space>
          <Button onClick={fetchShops}>刷新</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            添加店铺
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={shops}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={editingShop ? "编辑店铺" : "添加店铺"}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="店铺名称"
            rules={[{ required: true, message: "请输入店铺名称" }]}
          >
            <Input placeholder="请输入店铺名称" />
          </Form.Item>
          <Form.Item
            name="platform"
            label="平台"
            rules={[{ required: true, message: "请选择平台" }]}
          >
            <Select
              options={PLATFORMS}
              placeholder="请选择平台"
              disabled={!!editingShop}
            />
          </Form.Item>
          {!editingShop && (
            <>
              <Form.Item
                name={["api_credentials", "client_id"]}
                label="Client ID"
              >
                <Input placeholder="API Client ID" />
              </Form.Item>
              <Form.Item name={["api_credentials", "api_key"]} label="API Key">
                <Input.Password placeholder="API Key" />
              </Form.Item>
            </>
          )}
          {editingShop && (
            <Form.Item name="status" label="状态">
              <Select
                options={[
                  { value: "active", label: "正常" },
                  { value: "inactive", label: "停用" },
                ]}
              />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
}
