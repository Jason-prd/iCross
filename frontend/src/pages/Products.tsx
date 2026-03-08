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
  Image,
  Pagination,
} from "antd";
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  ExportOutlined,
  ImportOutlined,
} from "@ant-design/icons";
import { productsApi } from "../services/api";

interface Product {
  id: string;
  master_sku: string;
  title: string;
  description?: string;
  main_image_url?: string;
  images: string[];
  category_id?: string;
  brand?: string;
  weight?: number;
  status: string;
  tags: string[];
  platforms: PlatformProduct[];
  created_at: string;
}

interface PlatformProduct {
  platform: string;
  platform_product_id: string;
  platform_sku?: string;
  platform_price?: number;
  platform_currency?: string;
  platform_stock: number;
  platform_status?: string;
}

const PRODUCT_STATUS = [
  { value: "active", label: "上架", color: "green" },
  { value: "inactive", label: "下架", color: "orange" },
  { value: "draft", label: "草稿", color: "default" },
];

const PLATFORMS: Record<string, string> = {
  ozon: "Ozon",
  amazon: "Amazon",
  shopify: "Shopify",
  aliexpress: "AliExpress",
  wildberries: "Wildberries",
};

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [form] = Form.useForm();

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await productsApi.getAll({
        page,
        limit: pageSize,
        q: searchText || undefined,
        status: statusFilter,
      });
      setProducts(res.data || []);
      setTotal(res.meta?.total || 0);
    } catch (error: any) {
      message.error(error.message || "获取商品列表失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [page, pageSize, statusFilter]);

  const handleSearch = () => {
    setPage(1);
    fetchProducts();
  };

  const handleCreate = () => {
    setEditingProduct(null);
    form.resetFields();
    form.setFieldsValue({
      status: "active",
      images: [],
      tags: [],
      attributes: {},
    });
    setModalOpen(true);
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    form.setFieldsValue({
      master_sku: product.master_sku,
      title: product.title,
      description: product.description,
      main_image_url: product.main_image_url,
      brand: product.brand,
      weight: product.weight,
      status: product.status,
    });
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await productsApi.delete(id);
      message.success("商品已删除");
      fetchProducts();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "删除失败");
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingProduct) {
        await productsApi.update(editingProduct.id, {
          title: values.title,
          description: values.description,
          main_image_url: values.main_image_url,
          brand: values.brand,
          weight: values.weight,
          status: values.status,
        });
        message.success("商品已更新");
      } else {
        await productsApi.create({
          master_sku: values.master_sku,
          title: values.title,
          description: values.description,
          main_image_url: values.main_image_url,
          brand: values.brand,
          weight: values.weight,
          status: values.status || "active",
        });
        message.success("商品已创建");
      }
      setModalOpen(false);
      fetchProducts();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "操作失败");
    }
  };

  const columns = [
    {
      title: "图片",
      dataIndex: "main_image_url",
      key: "image",
      width: 80,
      render: (url: string) =>
        url ? (
          <Image
            src={url}
            width={50}
            height={50}
            style={{ objectFit: "cover" }}
            fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
          />
        ) : (
          "-"
        ),
    },
    {
      title: "商品信息",
      key: "info",
      render: (_: any, record: Product) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 500 }}>{record.title}</span>
          <span style={{ color: "#999", fontSize: 12 }}>
            SKU: {record.master_sku}
          </span>
          {record.brand && <Tag>{record.brand}</Tag>}
        </Space>
      ),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 80,
      render: (status: string) => {
        const s = PRODUCT_STATUS.find((item) => item.value === status);
        return <Tag color={s?.color || "default"}>{s?.label || status}</Tag>;
      },
    },
    {
      title: "平台信息",
      dataIndex: "platforms",
      key: "platforms",
      render: (platforms: PlatformProduct[]) => (
        <Space wrap>
          {platforms.length > 0
            ? platforms.map((p, idx) => (
                <Tag key={idx} color="blue">
                  {PLATFORMS[p.platform] || p.platform}: {p.platform_stock}件
                  {p.platform_price && ` ¥${p.platform_price}`}
                </Tag>
              ))
            : "-"}
        </Space>
      ),
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 120,
      render: (time: string) => new Date(time).toLocaleDateString("zh-CN"),
    },
    {
      title: "操作",
      key: "action",
      width: 150,
      render: (_: any, record: Product) => (
        <Space>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此商品吗？"
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
      <Space
        style={{
          marginBottom: 16,
          justifyContent: "space-between",
          width: "100%",
        }}
      >
        <Space>
          <Input.Search
            placeholder="搜索商品名称或SKU..."
            prefix={<SearchOutlined />}
            style={{ width: 300 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onSearch={handleSearch}
            enterButton
          />
          <Select
            placeholder="状态筛选"
            style={{ width: 120 }}
            value={statusFilter}
            onChange={(v) => {
              setStatusFilter(v);
              setPage(1);
            }}
            allowClear
            options={PRODUCT_STATUS.map((s) => ({
              value: s.value,
              label: s.label,
            }))}
          />
        </Space>
        <Space>
          <Button icon={<ImportOutlined />}>批量导入</Button>
          <Button icon={<ExportOutlined />}>导出</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            添加商品
          </Button>
        </Space>
      </Space>

      <Table
        columns={columns}
        dataSource={products}
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
        title={editingProduct ? "编辑商品" : "添加商品"}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
        width={600}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="master_sku"
            label="主SKU"
            rules={[{ required: true, message: "请输入主SKU" }]}
          >
            <Input placeholder="请输入主SKU" disabled={!!editingProduct} />
          </Form.Item>
          <Form.Item
            name="title"
            label="商品名称"
            rules={[{ required: true, message: "请输入商品名称" }]}
          >
            <Input placeholder="请输入商品名称" />
          </Form.Item>
          <Form.Item name="description" label="商品描述">
            <Input.TextArea rows={3} placeholder="请输入商品描述" />
          </Form.Item>
          <Form.Item name="main_image_url" label="主图URL">
            <Input placeholder="请输入主图URL" />
          </Form.Item>
          <Form.Item name="brand" label="品牌">
            <Input placeholder="请输入品牌" />
          </Form.Item>
          <Form.Item name="weight" label="重量(kg)">
            <Input type="number" placeholder="请输入重量" />
          </Form.Item>
          <Form.Item name="status" label="状态">
            <Select
              options={PRODUCT_STATUS.map((s) => ({
                value: s.value,
                label: s.label,
              }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
