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
  InputNumber,
  message,
  Pagination,
  Card,
  Statistic,
  Row,
  Col,
  Tabs,
} from "antd";
import {
  EditOutlined,
  DatabaseOutlined,
  WarningOutlined,
  SyncOutlined,
  ShopOutlined,
} from "@ant-design/icons";
import { inventoryApi, ozonApi, shopsApi } from "../services/api";

interface InventoryItem {
  product_id: string;
  product_title: string;
  product_sku: string;
  variant_id?: string;
  warehouses: WarehouseStock[];
  total_quantity: number;
  total_reserved: number;
  total_available: number;
  is_low_stock: boolean;
}

interface WarehouseStock {
  warehouse_id: string;
  warehouse_name: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  safety_stock: number;
  last_updated?: string;
}

interface Warehouse {
  id: string;
  name: string;
  code: string;
  type: string;
  status: string;
}

interface OzonWarehouse {
  warehouse_id: string;
  name: string;
  is_fbos: boolean;
  is_fbs: boolean;
  is_premium: boolean;
  type?: string;
  address?: Record<string, any>;
}

interface OzonDeliveryMethod {
  delivery_method_id: string;
  name: string;
  warehouse_id: string;
  warehouse_name?: string;
  price: number;
}

interface Shop {
  id: string;
  name: string;
  platform: string;
}

export default function Inventory() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(false);
  const [adjustModalOpen, setAdjustModalOpen] = useState(false);
  const [warehouseModalOpen, setWarehouseModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [adjustForm] = Form.useForm();
  const [warehouseForm] = Form.useForm();

  const [activeTab, setActiveTab] = useState("local");
  const [ozonWarehouses, setOzonWarehouses] = useState<OzonWarehouse[]>([]);
  const [ozonDeliveryMethods, setOzonDeliveryMethods] = useState<OzonDeliveryMethod[]>([]);
  const [ozonShops, setOzonShops] = useState<Shop[]>([]);
  const [selectedOzonShopId, setSelectedOzonShopId] = useState<string>("");
  const [ozonLoading, setOzonLoading] = useState(false);
  const [priceStockModalOpen, setPriceStockModalOpen] = useState(false);
  const [priceStockForm] = Form.useForm();

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const res = await inventoryApi.getAll({
        page,
        limit: pageSize,
        low_stock: lowStockOnly || undefined,
      });
      setInventory(res.data || []);
      setTotal(res.meta?.total || 0);
    } catch (error: any) {
      message.error(error.message || "获取库存列表失败");
    } finally {
      setLoading(false);
    }
  };

  const fetchWarehouses = async () => {
    try {
      const res = await inventoryApi.getWarehouses();
      setWarehouses(res.data || []);
    } catch (error: any) {
      console.error("Failed to fetch warehouses:", error);
    }
  };

  const fetchOzonShops = async () => {
    try {
      const res = await shopsApi.getAll({ platform: "ozon" });
      setOzonShops(res.data || []);
      if ((res.data || []).length > 0 && !selectedOzonShopId) {
        setSelectedOzonShopId(res.data[0].id);
      }
    } catch (error: any) {
      console.error("Failed to fetch Ozon shops:", error);
    }
  };

  const fetchOzonWarehouses = async () => {
    if (!selectedOzonShopId) return;
    setOzonLoading(true);
    try {
      const res = await ozonApi.getWarehouses(selectedOzonShopId);
      setOzonWarehouses(res.data || []);
    } catch (error: any) {
      message.error(error.message || "获取Ozon仓库失败");
    } finally {
      setOzonLoading(false);
    }
  };

  const fetchOzonDeliveryMethods = async () => {
    if (!selectedOzonShopId) return;
    setOzonLoading(true);
    try {
      const res = await ozonApi.getDeliveryMethods();
      setOzonDeliveryMethods(res.data || []);
    } catch (error: any) {
      message.error(error.message || "获取配送方式失败");
    } finally {
      setOzonLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
    fetchWarehouses();
    fetchOzonShops();
  }, [page, pageSize, lowStockOnly]);

  useEffect(() => {
    if (activeTab === "ozon" && selectedOzonShopId) {
      fetchOzonWarehouses();
      fetchOzonDeliveryMethods();
    }
  }, [activeTab, selectedOzonShopId]);

  const handleAdjust = (item: InventoryItem) => {
    setSelectedItem(item);
    adjustForm.resetFields();
    adjustForm.setFieldsValue({
      adjustment_type: "adjustment",
    });
    setAdjustModalOpen(true);
  };

  const handleAdjustSubmit = async (values: any) => {
    if (!selectedItem) return;
    try {
      const warehouseId =
        values.warehouse_id || selectedItem.warehouses[0]?.warehouse_id;
      if (!warehouseId) {
        message.error("请选择仓库");
        return;
      }
      await inventoryApi.adjust({
        product_id: selectedItem.product_id,
        warehouse_id: warehouseId,
        adjustment_type: values.adjustment_type,
        quantity_change: values.quantity_change,
        reason: values.reason,
      });
      message.success("库存调整成功");
      setAdjustModalOpen(false);
      fetchInventory();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "库存调整失败");
    }
  };

  const handleCreateWarehouse = async (values: any) => {
    try {
      await inventoryApi.createWarehouse(values);
      message.success("仓库创建成功");
      setWarehouseModalOpen(false);
      fetchWarehouses();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "创建仓库失败");
    }
  };

  const handleUpdateOzonPrices = async (values: any) => {
    if (!selectedOzonShopId) {
      message.warning("请先选择Ozon店铺");
      return;
    }
    setOzonLoading(true);
    try {
      const items = values.items.split("\n").filter((line: string) => line.trim()).map((line: string) => {
        const parts = line.split(",").map(p => p.trim());
        return {
          offer_id: parts[0],
          price: parseFloat(parts[1]),
          old_price: parts[2] ? parseFloat(parts[2]) : undefined,
        };
      });

      const res = await ozonApi.updateProductPrices(items, selectedOzonShopId);
      message.success(res.data.message || "价格更新任务已提交");
      setPriceStockModalOpen(false);
      priceStockForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "价格更新失败");
    } finally {
      setOzonLoading(false);
    }
  };

  const handleUpdateOzonStocks = async (values: any) => {
    if (!selectedOzonShopId) {
      message.warning("请先选择Ozon店铺");
      return;
    }
    setOzonLoading(true);
    try {
      const items = values.items.split("\n").filter((line: string) => line.trim()).map((line: string) => {
        const parts = line.split(",").map(p => p.trim());
        return {
          offer_id: parts[0],
          stock: parseInt(parts[1]),
          warehouse_id: parts[2] || undefined,
        };
      });

      const res = await ozonApi.updateProductStocks(items, selectedOzonShopId);
      message.success(res.data.message || "库存更新任务已提交");
      setPriceStockModalOpen(false);
      priceStockForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "库存更新失败");
    } finally {
      setOzonLoading(false);
    }
  };

  const lowStockCount = inventory.filter((item) => item.is_low_stock).length;

  const columns = [
    {
      title: "商品",
      key: "product",
      render: (_: any, record: InventoryItem) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 500 }}>{record.product_title}</span>
          <span style={{ color: "#999", fontSize: 12 }}>
            SKU: {record.product_sku}
          </span>
        </Space>
      ),
    },
    {
      title: "总库存",
      dataIndex: "total_quantity",
      key: "total_quantity",
      render: (qty: number, record: InventoryItem) => (
        <Space>
          <span
            style={{
              fontWeight: 500,
              color: record.is_low_stock ? "#f5222d" : undefined,
            }}
          >
            {qty}
          </span>
          {record.is_low_stock && (
            <WarningOutlined style={{ color: "#f5222d" }} />
          )}
        </Space>
      ),
    },
    {
      title: "可用库存",
      dataIndex: "total_available",
      key: "total_available",
      render: (qty: number) => (
        <Tag color={qty > 0 ? "green" : "red"}>{qty}</Tag>
      ),
    },
    {
      title: "预留库存",
      dataIndex: "total_reserved",
      key: "total_reserved",
      render: (qty: number) => qty,
    },
    {
      title: "库存分布",
      dataIndex: "warehouses",
      key: "warehouses",
      render: (warehouses: WarehouseStock[]) => (
        <Space wrap>
          {warehouses.map((w, idx) => (
            <Tag
              key={idx}
              color={w.quantity <= w.safety_stock ? "red" : "blue"}
            >
              {w.warehouse_name}: {w.quantity}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: InventoryItem) => (
        <Button
          size="small"
          icon={<EditOutlined />}
          onClick={() => handleAdjust(record)}
        >
          调整
        </Button>
      ),
    },
  ];

  const ozonWarehouseColumns = [
    {
      title: "仓库ID",
      dataIndex: "warehouse_id",
      key: "warehouse_id",
    },
    {
      title: "仓库名称",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "类型",
      key: "type",
      render: (_: any, record: OzonWarehouse) => (
        <Space>
          {record.is_fbos && <Tag color="purple">FBOS</Tag>}
          {record.is_fbs && <Tag color="blue">FBS</Tag>}
          {record.is_premium && <Tag color="gold">Premium</Tag>}
        </Space>
      ),
    },
    {
      title: "仓库地址",
      key: "address",
      render: (_: any, record: OzonWarehouse) => (
        record.address ? `${record.address.city || ""}, ${record.address.region || ""}` : "-"
      ),
    },
  ];

  const ozonDeliveryColumns = [
    {
      title: "配送方式ID",
      dataIndex: "delivery_method_id",
      key: "delivery_method_id",
    },
    {
      title: "配送方式名称",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "仓库",
      dataIndex: "warehouse_name",
      key: "warehouse_name",
    },
    {
      title: "价格",
      dataIndex: "price",
      key: "price",
      render: (price: number) => `¥${price}`,
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
        <h1 style={{ margin: 0 }}>库存管理</h1>
        <Space>
          <Button
            icon={<DatabaseOutlined />}
            onClick={() => setWarehouseModalOpen(true)}
          >
            添加仓库
          </Button>
        </Space>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane tab="本地库存" key="local">
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Card size="small">
                <Statistic title="总SKU数" value={total} />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="库存预警"
                  value={lowStockCount}
                  valueStyle={{ color: lowStockCount > 0 ? "#f5222d" : "#52c41a" }}
                  prefix={lowStockCount > 0 ? <WarningOutlined /> : null}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic title="仓库数量" value={warehouses.length} />
              </Card>
            </Col>
          </Row>

          <Space style={{ marginBottom: 16 }}>
            <Button
              type={lowStockOnly ? "primary" : "default"}
              danger={lowStockOnly}
              onClick={() => {
                setLowStockOnly(!lowStockOnly);
                setPage(1);
              }}
            >
              {lowStockOnly ? "显示全部" : "仅显示低库存"}
            </Button>
          </Space>

          <Table
            columns={columns}
            dataSource={inventory}
            rowKey="product_id"
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
        </Tabs.TabPane>

        <Tabs.TabPane tab={<span><ShopOutlined /> Ozon仓库</span>} key="ozon">
          <div style={{ marginBottom: 16 }}>
            <Space>
              <Select
                placeholder="选择Ozon店铺"
                style={{ width: 200 }}
                value={selectedOzonShopId}
                onChange={setSelectedOzonShopId}
                options={ozonShops.map(shop => ({
                  value: shop.id,
                  label: shop.name,
                }))}
              />
              <Button
                icon={<SyncOutlined />}
                onClick={() => {
                  fetchOzonWarehouses();
                  fetchOzonDeliveryMethods();
                }}
                loading={ozonLoading}
              >
                刷新
              </Button>
              <Button
                type="primary"
                onClick={() => {
                  priceStockForm.resetFields();
                  setPriceStockModalOpen(true);
                }}
              >
                批量更新价格/库存
              </Button>
            </Space>
          </div>

          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Card title="Ozon仓库列表" size="small">
                <Table
                  columns={ozonWarehouseColumns}
                  dataSource={ozonWarehouses}
                  rowKey="warehouse_id"
                  loading={ozonLoading}
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
            <Col span={12}>
              <Card title="配送方式列表" size="small">
                <Table
                  columns={ozonDeliveryColumns}
                  dataSource={ozonDeliveryMethods}
                  rowKey="delivery_method_id"
                  loading={ozonLoading}
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
          </Row>
        </Tabs.TabPane>
      </Tabs>

      <Modal
        title="库存调整"
        open={adjustModalOpen}
        onCancel={() => setAdjustModalOpen(false)}
        onOk={() => adjustForm.submit()}
      >
        {selectedItem && (
          <div style={{ marginBottom: 16 }}>
            <strong>{selectedItem.product_title}</strong> (SKU:{" "}
            {selectedItem.product_sku})
          </div>
        )}
        <Form form={adjustForm} layout="vertical" onFinish={handleAdjustSubmit}>
          {selectedItem && selectedItem.warehouses.length > 1 && (
            <Form.Item
              name="warehouse_id"
              label="仓库"
              rules={[{ required: true, message: "请选择仓库" }]}
            >
              <Select
                options={selectedItem.warehouses.map((w) => ({
                  value: w.warehouse_id,
                  label: `${w.warehouse_name} (当前: ${w.quantity})`,
                }))}
              />
            </Form.Item>
          )}
          <Form.Item
            name="adjustment_type"
            label="调整类型"
            rules={[{ required: true }]}
          >
            <Select
              options={[
                { value: "adjustment", label: "库存调整" },
                { value: "receipt", label: "入库" },
                { value: "shipment", label: "出库" },
                { value: "return", label: "退货入库" },
                { value: "damage", label: "损耗" },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="quantity_change"
            label="数量变化"
            rules={[{ required: true, message: "请输入数量变化" }]}
            extra="正数为增加，负数为减少"
          >
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="reason" label="调整原因">
            <Input.TextArea rows={2} placeholder="请输入调整原因" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="添加仓库"
        open={warehouseModalOpen}
        onCancel={() => setWarehouseModalOpen(false)}
        onOk={() => warehouseForm.submit()}
      >
        <Form
          form={warehouseForm}
          layout="vertical"
          onFinish={handleCreateWarehouse}
        >
          <Form.Item
            name="name"
            label="仓库名称"
            rules={[{ required: true, message: "请输入仓库名称" }]}
          >
            <Input placeholder="请输入仓库名称" />
          </Form.Item>
          <Form.Item
            name="code"
            label="仓库编码"
            rules={[{ required: true, message: "请输入仓库编码" }]}
          >
            <Input placeholder="请输入仓库编码" />
          </Form.Item>
          <Form.Item name="type" label="仓库类型">
            <Select
              options={[
                { value: "physical", label: "实体仓库" },
                { value: "virtual", label: "虚拟仓库" },
              ]}
              defaultValue="physical"
            />
          </Form.Item>
          <Form.Item name="capacity" label="容量">
            <InputNumber
              style={{ width: "100%" }}
              placeholder="仓库容量（可选）"
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="批量更新Ozon商品价格/库存"
        open={priceStockModalOpen}
        onCancel={() => setPriceStockModalOpen(false)}
        footer={null}
        width={600}
      >
        <Form form={priceStockForm} layout="vertical">
          <Form.Item name="update_type" label="更新类型" initialValue="price">
            <Select>
              <Select.Option value="price">更新价格</Select.Option>
              <Select.Option value="stock">更新库存</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="items"
            label="数据（每行一条，格式为: offer_id,price[,old_price] 或 offer_id,stock[,warehouse_id]）"
            rules={[{ required: true, message: "请输入数据" }]}
          >
            <Input.TextArea
              rows={8}
              placeholder="例如：&#10;SKU001,1000,900&#10;SKU002,2000,1800&#10;或&#10;SKU001,100&#10;SKU002,200,warehouse123"
            />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button
                type="primary"
                onClick={() => {
                  const updateType = priceStockForm.getFieldValue("update_type");
                  if (updateType === "price") {
                    handleUpdateOzonPrices(priceStockForm.getFieldsValue());
                  } else {
                    handleUpdateOzonStocks(priceStockForm.getFieldsValue());
                  }
                }}
                loading={ozonLoading}
              >
                提交更新
              </Button>
              <Button onClick={() => setPriceStockModalOpen(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
        <div style={{ color: "#999", fontSize: 12, marginTop: 8 }}>
          <p>提示：</p>
          <ul>
            <li>更新价格格式：offer_id,新价格,原价（原价可选）</li>
            <li>更新库存格式：offer_id,库存数量,仓库ID（仓库ID可选）</li>
            <li>每行一条数据，不要包含中文逗号</li>
          </ul>
        </div>
      </Modal>
    </div>
  );
}
