import { useState, useEffect } from "react";
import {
  Table,
  Button,
  Space,
  Tag,
  Select,
  Modal,
  Descriptions,
  Form,
  Input,
  message,
  Pagination,
} from "antd";
import {
  EyeOutlined,
  TruckOutlined,
  ExportOutlined,
  SyncOutlined,
} from "@ant-design/icons";
import { ordersApi, ozonApi, shopsApi } from "../services/api";
import dayjs from "dayjs";

interface OrderItem {
  id: string;
  product_id: string;
  variant_id?: string;
  title: string;
  sku: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

interface Order {
  id: string;
  order_number: string;
  platform: string;
  shop_id: string;
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  shipping_address: Record<string, any>;
  currency: string;
  subtotal_amount: number;
  shipping_amount: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  payment_status: string;
  fulfillment_status: string;
  shipping_carrier?: string;
  shipping_tracking_number?: string;
  status: string;
  notes?: string;
  extra_data?: Record<string, any>;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

interface Shop {
  id: string;
  name: string;
  platform: string;
  platform_shop_name?: string;
  status: string;
}

const ORDER_STATUS: Record<string, { label: string; color: string }> = {
  pending: { label: "待处理", color: "orange" },
  confirmed: { label: "已确认", color: "blue" },
  processing: { label: "处理中", color: "cyan" },
  shipped: { label: "已发货", color: "geekblue" },
  delivered: { label: "已送达", color: "green" },
  cancelled: { label: "已取消", color: "red" },
  refunded: { label: "已退款", color: "volcano" },
};

const PAYMENT_STATUS: Record<string, { label: string; color: string }> = {
  pending: { label: "待付款", color: "orange" },
  paid: { label: "已付款", color: "green" },
  partially_refunded: { label: "部分退款", color: "blue" },
  refunded: { label: "已退款", color: "red" },
};

const FULFILLMENT_STATUS: Record<string, { label: string; color: string }> = {
  unfulfilled: { label: "未发货", color: "orange" },
  partial: { label: "部分发货", color: "blue" },
  fulfilled: { label: "已发货", color: "green" },
};

const PLATFORMS: Record<string, string> = {
  ozon: "Ozon",
  amazon: "Amazon",
  shopify: "Shopify",
  aliexpress: "AliExpress",
  wildberries: "Wildberries",
};

const FULFILLMENT_TYPE: Record<string, string> = {
  fbo: "FBO (平台履约)",
  fbs: "FBS (卖家履约)",
};

export default function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [shipModalOpen, setShipModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [paymentFilter, setPaymentFilter] = useState<string | undefined>();
  const [fulfillmentFilter, setFulfillmentFilter] = useState<
    string | undefined
  >();
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [shipForm] = Form.useForm();
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncModalOpen, setSyncModalOpen] = useState(false);
  const [daysBack, setDaysBack] = useState(7);
  const [selectedShopIds, setSelectedShopIds] = useState<string[]>([]);
  const [ozonShops, setOzonShops] = useState<Shop[]>([]);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await ordersApi.getAll({
        page,
        limit: pageSize,
        status: statusFilter,
        payment_status: paymentFilter,
        fulfillment_status: fulfillmentFilter,
      });
      setOrders(res.data || []);
      setTotal(res.meta?.total || 0);
    } catch (error: any) {
      message.error(error.message || "获取订单列表失败");
    } finally {
      setLoading(false);
    }
  };

  const fetchOzonShops = async () => {
    try {
      const res = await shopsApi.getAll({ platform: "ozon" });
      setOzonShops(res.data || []);
      if ((res.data || []).length > 0) {
        setSelectedShopIds([res.data[0].id]);
      } else {
        setSelectedShopIds([]);
      }
    } catch (error: any) {
      message.error(error.message || "获取Ozon店铺失败");
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, pageSize, statusFilter, paymentFilter, fulfillmentFilter]);

  const handleViewDetail = async (order: Order) => {
    try {
      const res = await ordersApi.getOne(order.id);
      setSelectedOrder(res.data);
      setDetailModalOpen(true);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "获取订单详情失败");
    }
  };

  const handleShip = (order: Order) => {
    setSelectedOrder(order);
    shipForm.resetFields();
    setShipModalOpen(true);
  };

  const handleShipSubmit = async (values: any) => {
    if (!selectedOrder) return;
    try {
      await ordersApi.updateStatus(selectedOrder.id, {
        status: "shipped",
        shipping_info: {
          carrier: values.carrier,
          tracking_number: values.tracking_number,
        },
        notes: values.notes,
      });
      message.success("发货成功");
      setShipModalOpen(false);
      fetchOrders();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "发货失败");
    }
  };

  const handleExport = () => {
    message.info("导出功能开发中...");
  };

  const handleSyncOzonOrders = async () => {
    if (selectedShopIds.length === 0) {
      message.warning("请至少选择一个Ozon店铺");
      return;
    }

    setSyncLoading(true);
    let totalSynced = 0;
    let totalUpdated = 0;
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const shopId of selectedShopIds) {
        try {
          const res = await ozonApi.syncOrders(shopId, daysBack);
          totalSynced += res.data.synced;
          totalUpdated += res.data.updated;
          successCount++;

          if (res.data.synced === 0 && res.data.updated === 0) {
            message.warning(
              `店铺 ${ozonShops.find((s) => s.id === shopId)?.name || shopId} 同步完成但无新订单，请检查店铺配置或订单状态`,
            );
          } else {
            message.success(
              `店铺 ${ozonShops.find((s) => s.id === shopId)?.name || shopId} 同步成功: ${res.data.synced}个新增, ${res.data.updated}个更新`,
            );
          }
        } catch (error: any) {
          errorCount++;
          message.error(
            `店铺 ${ozonShops.find((s) => s.id === shopId)?.name || shopId} 同步失败: ${error.response?.data?.detail || "未知错误"}`,
          );
        }
      }

      // 汇总信息
      if (successCount > 0) {
        message.success(
          `同步完成: ${successCount}个店铺成功, ${errorCount}个店铺失败. 总计: ${totalSynced}个新增订单, ${totalUpdated}个更新订单`,
        );
      } else {
        message.error("所有店铺同步失败");
      }

      setSyncModalOpen(false);
      // 刷新订单列表
      fetchOrders();
    } catch (error: any) {
      message.error(
        `同步过程出错: ${error.response?.data?.detail || "未知错误"}`,
      );
    } finally {
      setSyncLoading(false);
    }
  };

  const columns = [
    {
      title: "订单号",
      dataIndex: "order_number",
      key: "order_number",
      render: (num: string) => (
        <span style={{ fontFamily: "monospace" }}>{num || "-"}</span>
      ),
    },
    {
      title: "客户",
      key: "customer",
      render: (_: any, record: Order) => (
        <Space direction="vertical" size={0}>
          <span>{record.customer_name || "-"}</span>
          <span style={{ color: "#999", fontSize: 12 }}>
            {record.customer_email || ""}
          </span>
        </Space>
      ),
    },
    {
      title: "金额",
      key: "amount",
      render: (_: any, record: Order) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 500 }}>
            {record.currency === "CNY" ? "¥" : record.currency}
            {record.total_amount.toFixed(2)}
          </span>
          <span style={{ color: "#999", fontSize: 12 }}>
            {record.items.length} 件商品
          </span>
        </Space>
      ),
    },
    {
      title: "订单状态",
      dataIndex: "status",
      key: "status",
      render: (status: string) => {
        const s = ORDER_STATUS[status];
        return <Tag color={s?.color || "default"}>{s?.label || status}</Tag>;
      },
    },
    {
      title: "付款状态",
      dataIndex: "payment_status",
      key: "payment_status",
      render: (status: string) => {
        const s = PAYMENT_STATUS[status];
        return <Tag color={s?.color || "default"}>{s?.label || status}</Tag>;
      },
    },
    {
      title: "发货状态",
      dataIndex: "fulfillment_status",
      key: "fulfillment_status",
      render: (status: string) => {
        const s = FULFILLMENT_STATUS[status];
        return <Tag color={s?.color || "default"}>{s?.label || status}</Tag>;
      },
    },
    {
      title: "平台",
      dataIndex: "platform",
      key: "platform",
      render: (platform: string) => (
        <Tag color="blue">{PLATFORMS[platform] || platform}</Tag>
      ),
    },
    {
      title: "履约类型",
      key: "fulfillment_type",
      render: (_: any, record: Order) => {
        const type = record.extra_data?.fulfillment_type;
        if (!type) return "-";
        return <Tag color={type === "fbo" ? "purple" : "orange"}>{FULFILLMENT_TYPE[type] || type}</Tag>;
      },
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 120,
      render: (time: string) => dayjs(time).format("MM-DD HH:mm"),
    },
    {
      title: "操作",
      key: "action",
      width: 150,
      render: (_: any, record: Order) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.fulfillment_status === "unfulfilled" &&
            record.payment_status === "paid" && (
              <Button
                size="small"
                type="primary"
                icon={<TruckOutlined />}
                onClick={() => handleShip(record)}
              >
                发货
              </Button>
            )}
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
        <h1 style={{ margin: 0 }}>订单管理</h1>
        <Space>
          <Button
            icon={<SyncOutlined />}
            onClick={() => {
              setSyncModalOpen(true);
              fetchOzonShops();
            }}
            loading={syncLoading}
            type="primary"
          >
            同步Ozon订单
          </Button>
          <Button icon={<ExportOutlined />} onClick={handleExport}>
            导出
          </Button>
        </Space>
      </div>

      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="订单状态"
          style={{ width: 120 }}
          value={statusFilter}
          onChange={(v) => {
            setStatusFilter(v);
            setPage(1);
          }}
          allowClear
          options={Object.entries(ORDER_STATUS).map(([value, { label }]) => ({
            value,
            label,
          }))}
        />
        <Select
          placeholder="付款状态"
          style={{ width: 120 }}
          value={paymentFilter}
          onChange={(v) => {
            setPaymentFilter(v);
            setPage(1);
          }}
          allowClear
          options={Object.entries(PAYMENT_STATUS).map(([value, { label }]) => ({
            value,
            label,
          }))}
        />
        <Select
          placeholder="发货状态"
          style={{ width: 120 }}
          value={fulfillmentFilter}
          onChange={(v) => {
            setFulfillmentFilter(v);
            setPage(1);
          }}
          allowClear
          options={Object.entries(FULFILLMENT_STATUS).map(
            ([value, { label }]) => ({ value, label }),
          )}
        />
        <Select
          placeholder="履约类型"
          style={{ width: 120 }}
          allowClear
          onChange={(v) => {
            // 通过 extra_data.fulfillment_type 过滤
            setPage(1);
            // 这里可以添加额外的过滤逻辑
          }}
          options={[
            { value: 'fbo', label: 'FBO' },
            { value: 'fbs', label: 'FBS' },
          ]}
        />
        <Button
          icon={<TruckOutlined />}
          onClick={async () => {
            try {
              const res = await ozonApi.getUnfulfilledPostings();
              message.success(`获取到 ${res.length} 个待发货订单`);
              // 可以将待发货订单显示在表格中
            } catch (e) {
              message.error('获取待发货订单失败');
            }
          }}
        >
          待发货订单
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={orders}
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
        title="订单详情"
        open={detailModalOpen}
        onCancel={() => setDetailModalOpen(false)}
        footer={null}
        width={700}
      >
        {selectedOrder && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="订单号" span={2}>
              {selectedOrder.order_number}
            </Descriptions.Item>
            <Descriptions.Item label="平台">
              {PLATFORMS[selectedOrder.platform] || selectedOrder.platform}
            </Descriptions.Item>
            <Descriptions.Item label="履约类型">
              {selectedOrder.extra_data?.fulfillment_type ? (
                <Tag color={selectedOrder.extra_data.fulfillment_type === "fbo" ? "purple" : "orange"}>
                  {FULFILLMENT_TYPE[selectedOrder.extra_data.fulfillment_type] || selectedOrder.extra_data.fulfillment_type}
                </Tag>
              ) : "-"}
            </Descriptions.Item>
            <Descriptions.Item label="订单状态">
              <Tag color={ORDER_STATUS[selectedOrder.status]?.color}>
                {ORDER_STATUS[selectedOrder.status]?.label}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="付款状态">
              <Tag color={PAYMENT_STATUS[selectedOrder.payment_status]?.color}>
                {PAYMENT_STATUS[selectedOrder.payment_status]?.label}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="发货状态">
              <Tag
                color={
                  FULFILLMENT_STATUS[selectedOrder.fulfillment_status]?.color
                }
              >
                {FULFILLMENT_STATUS[selectedOrder.fulfillment_status]?.label}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="客户姓名">
              {selectedOrder.customer_name || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="客户邮箱">
              {selectedOrder.customer_email || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="客户电话">
              {selectedOrder.customer_phone || "-"}
            </Descriptions.Item>
            <Descriptions.Item label="收货地址" span={2}>
              {selectedOrder.shipping_address?.city || ""}{" "}
              {selectedOrder.shipping_address?.address || ""}{" "}
              {selectedOrder.shipping_address?.region || ""}
            </Descriptions.Item>
            <Descriptions.Item label="商品小计">
              {selectedOrder.currency === "CNY" ? "¥" : selectedOrder.currency}
              {selectedOrder.subtotal_amount.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="运费">
              {selectedOrder.currency === "CNY" ? "¥" : selectedOrder.currency}
              {selectedOrder.shipping_amount.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="税费">
              {selectedOrder.currency === "CNY" ? "¥" : selectedOrder.currency}
              {selectedOrder.tax_amount.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="折扣">
              -{selectedOrder.currency === "CNY" ? "¥" : selectedOrder.currency}
              {selectedOrder.discount_amount.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="订单总额" span={2}>
              <span
                style={{ fontSize: 16, fontWeight: "bold", color: "#f5222d" }}
              >
                {selectedOrder.currency === "CNY"
                  ? "¥"
                  : selectedOrder.currency}
                {selectedOrder.total_amount.toFixed(2)}
              </span>
            </Descriptions.Item>
            {selectedOrder.shipping_carrier && (
              <Descriptions.Item label="物流公司">
                {selectedOrder.shipping_carrier}
              </Descriptions.Item>
            )}
            {selectedOrder.shipping_tracking_number && (
              <Descriptions.Item label="物流单号">
                {selectedOrder.shipping_tracking_number}
              </Descriptions.Item>
            )}
            <Descriptions.Item label="创建时间">
              {dayjs(selectedOrder.created_at).format("YYYY-MM-DD HH:mm:ss")}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {dayjs(selectedOrder.updated_at).format("YYYY-MM-DD HH:mm:ss")}
            </Descriptions.Item>
            {selectedOrder.notes && (
              <Descriptions.Item label="备注" span={2}>
                {selectedOrder.notes}
              </Descriptions.Item>
            )}
          </Descriptions>
        )}

        {selectedOrder && selectedOrder.items.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <h4>商品明细</h4>
            <Table
              size="small"
              columns={[
                { title: "商品", dataIndex: "title", key: "title" },
                { title: "SKU", dataIndex: "sku", key: "sku" },
                { title: "数量", dataIndex: "quantity", key: "quantity" },
                {
                  title: "单价",
                  dataIndex: "unit_price",
                  key: "unit_price",
                  render: (v) => `¥${v}`,
                },
                {
                  title: "小计",
                  dataIndex: "subtotal",
                  key: "subtotal",
                  render: (v) => `¥${v}`,
                },
              ]}
              dataSource={selectedOrder.items}
              rowKey="id"
              pagination={false}
            />
          </div>
        )}
      </Modal>

      <Modal
        title="订单发货"
        open={shipModalOpen}
        onCancel={() => setShipModalOpen(false)}
        onOk={() => shipForm.submit()}
      >
        <Form form={shipForm} layout="vertical" onFinish={handleShipSubmit}>
          <Form.Item
            name="carrier"
            label="物流公司"
            rules={[{ required: true, message: "请输入物流公司" }]}
          >
            <Input placeholder="如：顺丰、中通、圆通等" />
          </Form.Item>
          <Form.Item
            name="tracking_number"
            label="物流单号"
            rules={[{ required: true, message: "请输入物流单号" }]}
          >
            <Input placeholder="请输入物流单号" />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={2} placeholder="发货备注（可选）" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="同步Ozon订单"
        open={syncModalOpen}
        onCancel={() => setSyncModalOpen(false)}
        onOk={handleSyncOzonOrders}
        okText="开始同步"
        cancelText="取消"
        confirmLoading={syncLoading}
        width={600}
      >
        <div style={{ padding: "20px 0" }}>
          <p>选择要同步的Ozon店铺和同步天数范围：</p>
          <Form layout="vertical">
            <Form.Item label="选择店铺" required>
              <Select
                mode="multiple"
                placeholder="请选择Ozon店铺"
                value={selectedShopIds}
                onChange={setSelectedShopIds}
                style={{ width: "100%" }}
                options={ozonShops.map((shop) => ({
                  label: `${shop.name} (${shop.platform_shop_name || "未绑定"})`,
                  value: shop.id,
                  disabled: shop.status !== "active",
                }))}
              />
              {ozonShops.length === 0 && (
                <p style={{ color: "#ff4d4f", marginTop: 8 }}>
                  未找到Ozon店铺，请先在店铺管理中添加Ozon店铺
                </p>
              )}
            </Form.Item>
            <Form.Item label="同步天数范围">
              <Select
                value={daysBack}
                onChange={(value) => setDaysBack(value)}
                style={{ width: "100%" }}
              >
                <Select.Option value={1}>最近1天</Select.Option>
                <Select.Option value={3}>最近3天</Select.Option>
                <Select.Option value={7}>最近7天</Select.Option>
                <Select.Option value={14}>最近14天</Select.Option>
                <Select.Option value={30}>最近30天</Select.Option>
              </Select>
            </Form.Item>
          </Form>
          <p style={{ color: "#999", fontSize: "12px", marginTop: "10px" }}>
            注意：同步过程可能需要几分钟时间，具体取决于订单数量。将依次同步每个选中的店铺。
          </p>
        </div>
      </Modal>
    </div>
  );
}
