// -*- coding: utf-8 -*-
/**
 * 代发订单页面
 * 显示代发订单信息
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Space, Input, Select, Row, Col, Statistic, Modal, Descriptions, Timeline, Progress } from 'antd';
import { EyeOutlined, SyncOutlined, ShopOutlined, DollarOutlined, CarOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Search } = Input;

interface DropshipOrder {
  id: string;
  platform_order_id: string;
  sku: string;
  quantity: number;
  sale_price: number;
  purchase_cost: number;
  shipping_cost: number;
  profit: number;
  profit_rate: number;
  status: string;
  supplier_order_id: string;
  tracking_number: string;
  shipping_carrier: string;
  order_placed_at: string;
  supplier_order_at: string;
  shipped_at: string;
  delivered_at: string;
}

const DropshipOrdersPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState<DropshipOrder[]>([]);
  const [filteredOrders, setFilteredOrders] = useState<DropshipOrder[]>([]);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedOrder, setSelectedOrder] = useState<DropshipOrder | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  // 模拟数据
  useEffect(() => {
    const mockData: DropshipOrder[] = [
      {
        id: '1',
        platform_order_id: '123456789',
        sku: 'SKU#0828104003-1',
        quantity: 1,
        sale_price: 899.00,
        purchase_cost: 580.00,
        shipping_cost: 20.00,
        profit: 299.00,
        profit_rate: 33.3,
        status: 'shipped',
        supplier_order_id: '1689-123456789',
        tracking_number: 'SF1234567890',
        shipping_carrier: '顺丰速运',
        order_placed_at: '2026-02-27 14:35:00',
        supplier_order_at: '2026-02-27 14:40:00',
        shipped_at: '2026-02-27 16:00:00',
        delivered_at: '',
      },
      {
        id: '2',
        platform_order_id: '123456790',
        sku: 'SKU#0829000219-1',
        quantity: 2,
        sale_price: 1590.00,
        purchase_cost: 1100.00,
        shipping_cost: 35.00,
        profit: 455.00,
        profit_rate: 28.6,
        status: 'processing',
        supplier_order_id: '1689-123456790',
        tracking_number: '',
        shipping_carrier: '',
        order_placed_at: '2026-02-27 16:50:00',
        supplier_order_at: '2026-02-27 16:55:00',
        shipped_at: '',
        delivered_at: '',
      },
      {
        id: '3',
        platform_order_id: '123456791',
        sku: 'SKU#0915222047-1',
        quantity: 1,
        sale_price: 2490.00,
        purchase_cost: 1800.00,
        shipping_cost: 25.00,
        profit: 665.00,
        profit_rate: 26.7,
        status: 'pending',
        supplier_order_id: '',
        tracking_number: '',
        shipping_carrier: '',
        order_placed_at: '2026-02-27 18:25:00',
        supplier_order_at: '',
        shipped_at: '',
        delivered_at: '',
      },
      {
        id: '4',
        platform_order_id: '123456788',
        sku: 'SKU#0828104003-1',
        quantity: 1,
        sale_price: 899.00,
        purchase_cost: 580.00,
        shipping_cost: 20.00,
        profit: 299.00,
        profit_rate: 33.3,
        status: 'delivered',
        supplier_order_id: '1689-123456788',
        tracking_number: 'SF1234567880',
        shipping_carrier: '顺丰速运',
        order_placed_at: '2026-02-26 10:00:00',
        supplier_order_at: '2026-02-26 10:05:00',
        shipped_at: '2026-02-26 12:00:00',
        delivered_at: '2026-02-27 14:00:00',
      },
    ];
    setOrders(mockData);
    setFilteredOrders(mockData);
  }, []);

  useEffect(() => {
    let filtered = orders;
    if (searchText) {
      filtered = filtered.filter(o => 
        o.platform_order_id.toLowerCase().includes(searchText.toLowerCase()) ||
        o.sku.toLowerCase().includes(searchText.toLowerCase()) ||
        o.tracking_number?.toLowerCase().includes(searchText.toLowerCase())
      );
    }
    if (statusFilter !== 'all') {
      filtered = filtered.filter(o => o.status === statusFilter);
    }
    setFilteredOrders(filtered);
  }, [searchText, statusFilter, orders]);

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      pending: { color: 'default', text: '待处理' },
      processing: { color: 'processing', text: '处理中' },
      shipped: { color: 'blue', text: '已发货' },
      delivered: { color: 'green', text: '已送达' },
      cancelled: { color: 'red', text: '已取消' },
    };
    const s = statusMap[status] || { color: 'default', text: status };
    return <Tag color={s.color}>{s.text}</Tag>;
  };

  const getProfitTag = (rate: number) => {
    if (rate >= 30) return <Tag color="green">高 {rate}%</Tag>;
    if (rate >= 15) return <Tag color="orange">中 {rate}%</Tag>;
    return <Tag color="red">低 {rate}%</Tag>;
  };

  const columns: ColumnsType<DropshipOrder> = [
    {
      title: 'Ozon订单号',
      dataIndex: 'platform_order_id',
      key: 'platform_order_id',
      width: 130,
    },
    {
      title: 'SKU',
      dataIndex: 'sku',
      key: 'sku',
      width: 160,
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 70,
    },
    {
      title: '销售价',
      dataIndex: 'sale_price',
      key: 'sale_price',
      width: 100,
      render: (price: number) => `₽${price?.toFixed(2) || 0}`,
    },
    {
      title: '采购成本',
      dataIndex: 'purchase_cost',
      key: 'purchase_cost',
      width: 100,
      render: (cost: number) => `¥${cost?.toFixed(2) || 0}`,
    },
    {
      title: '运费',
      dataIndex: 'shipping_cost',
      key: 'shipping_cost',
      width: 80,
      render: (cost: number) => `¥${cost?.toFixed(2) || 0}`,
    },
    {
      title: '利润',
      dataIndex: 'profit',
      key: 'profit',
      width: 100,
      render: (profit: number) => (
        <span style={{ color: profit > 0 ? '#52c41a' : '#ff4d4f' }}>
          ¥{profit?.toFixed(2) || 0}
        </span>
      ),
    },
    {
      title: '利润率',
      dataIndex: 'profit_rate',
      key: 'profit_rate',
      width: 90,
      render: (rate: number) => getProfitTag(rate),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 90,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '物流单号',
      dataIndex: 'tracking_number',
      key: 'tracking_number',
      width: 150,
    },
    {
      title: '下单时间',
      dataIndex: 'order_placed_at',
      key: 'order_placed_at',
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedOrder(record);
            setDetailVisible(true);
          }}
        >
          详情
        </Button>
      ),
    },
  ];

  // 统计
  const pendingCount = orders.filter(o => o.status === 'pending').length;
  const processingCount = orders.filter(o => o.status === 'processing').length;
  const shippedCount = orders.filter(o => o.status === 'shipped').length;
  const totalProfit = orders.reduce((sum, o) => sum + o.profit, 0);
  const avgProfit = orders.length > 0 ? totalProfit / orders.length : 0;

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="代发订单总数" 
              value={orders.length} 
              prefix={<ShopOutlined />} 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="待处理" 
              value={pendingCount} 
              valueStyle={{ color: '#faad14' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已发货" 
              value={shippedCount} 
              valueStyle={{ color: '#1890ff' }}
              prefix={<CarOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="总利润" 
              value={totalProfit} 
              suffix="¥"
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Card 
        title="代发订单列表"
        extra={
          <Space>
            <Search
              placeholder="搜索订单号/SKU/物流单号"
              onSearch={setSearchText}
              style={{ width: 250 }}
              allowClear
            />
            <Select
              placeholder="订单状态"
              style={{ width: 100 }}
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { value: 'all', label: '全部' },
                { value: 'pending', label: '待处理' },
                { value: 'processing', label: '处理中' },
                { value: 'shipped', label: '已发货' },
                { value: 'delivered', label: '已送达' },
              ]}
            />
            <Button icon={<SyncOutlined />}>同步代发</Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={filteredOrders}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1500 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      <Modal
        title="代发订单详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {selectedOrder && (
          <>
            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="Ozon订单号" span={2}>
                {selectedOrder.platform_order_id}
              </Descriptions.Item>
              <Descriptions.Item label="SKU">
                {selectedOrder.sku}
              </Descriptions.Item>
              <Descriptions.Item label="数量">
                {selectedOrder.quantity}
              </Descriptions.Item>
              <Descriptions.Item label="销售价">
                ₽{selectedOrder.sale_price.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="采购成本">
                ¥{selectedOrder.purchase_cost.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="运费">
                ¥{selectedOrder.shipping_cost.toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="利润">
                <span style={{ color: selectedOrder.profit > 0 ? '#52c41a' : '#ff4d4f' }}>
                  ¥{selectedOrder.profit.toFixed(2)}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="利润率">
                {getProfitTag(selectedOrder.profit_rate)}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                {getStatusTag(selectedOrder.status)}
              </Descriptions.Item>
              <Descriptions.Item label="代发商订单号">
                {selectedOrder.supplier_order_id || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="物流单号" span={2}>
                {selectedOrder.tracking_number || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="物流公司">
                {selectedOrder.shipping_carrier || '-'}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 24 }}>
              <h4>订单流程</h4>
              <Timeline
                items={[
                  { 
                    color: 'green',
                    children: `Ozon下单 - ${selectedOrder.order_placed_at}`,
                  },
                  { 
                    color: selectedOrder.supplier_order_at ? 'green' : 'gray',
                    children: selectedOrder.supplier_order_at 
                      ? `代发下单 - ${selectedOrder.supplier_order_at}` 
                      : '等待代发下单',
                  },
                  { 
                    color: selectedOrder.shipped_at ? 'green' : 'gray',
                    children: selectedOrder.shipped_at 
                      ? `已发货 - ${selectedOrder.shipped_at}` 
                      : '等待发货',
                  },
                  { 
                    color: selectedOrder.delivered_at ? 'green' : 'gray',
                    children: selectedOrder.delivered_at 
                      ? `已送达 - ${selectedOrder.delivered_at}` 
                      : '等待送达',
                  },
                ]}
              />
            </div>
          </>
        )}
      </Modal>
    </div>
  );
};

export default DropshipOrdersPage;
