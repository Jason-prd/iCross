// -*- coding: utf-8 -*-
/**
 * 订单管理页面
 * 显示Ozon订单信息
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Space, Input, Select, Row, Col, Statistic, Modal, Descriptions, DatePicker, Tabs } from 'antd';
import { EyeOutlined, SyncOutlined, CarOutlined, DollarOutlined, ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { RangePicker } = DatePicker;
const { Search } = Input;

interface Order {
  id: string;
  order_number: string;
  platform_order_id: string;
  customer_name: string;
  total_amount: number;
  status: string;
  fulfillment_status: string;
  payment_status: string;
  created_at: string;
  products: Array<{ sku: string; name: string; quantity: number; price: number }>;
  shipping_address: {
    city: string;
    region: string;
    postal_code: string;
  };
}

const OrdersPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [orders, setOrders] = useState<Order[]>([]);
  const [filteredOrders, setFilteredOrders] = useState<Order[]>([]);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  // 模拟数据
  useEffect(() => {
    const mockData: Order[] = [
      {
        id: '1',
        order_number: '123456789-1',
        platform_order_id: '123456789',
        customer_name: 'Ivan Petrov',
        total_amount: 1590.00,
        status: 'completed',
        fulfillment_status: 'delivered',
        payment_status: 'paid',
        created_at: '2026-02-27 14:30:00',
        products: [
          { sku: 'SKU#0828104003-1', name: 'iPhone手机壳', quantity: 1, price: 899.00 },
          { sku: 'SKU#0828104003-2', name: 'iPhone手机壳', quantity: 1, price: 691.00 },
        ],
        shipping_address: {
          city: 'Москва',
          region: 'Москва',
          postal_code: '101000',
        },
      },
      {
        id: '2',
        order_number: '123456790-1',
        platform_order_id: '123456790',
        customer_name: 'Anna Smirnova',
        total_amount: 899.00,
        status: 'processing',
        fulfillment_status: 'awaiting_delivery',
        payment_status: 'paid',
        created_at: '2026-02-27 16:45:00',
        products: [
          { sku: 'SKU#0829000219-1', name: '合金车模', quantity: 1, price: 899.00 },
        ],
        shipping_address: {
          city: 'Санкт-Петербург',
          region: 'Санкт-Петербург',
          postal_code: '191000',
        },
      },
      {
        id: '3',
        order_number: '123456791-1',
        platform_order_id: '123456791',
        customer_name: 'Dmitry Ivanov',
        total_amount: 2490.00,
        status: 'pending',
        fulfillment_status: 'awaiting_shipment',
        payment_status: 'paid',
        created_at: '2026-02-27 18:20:00',
        products: [
          { sku: 'SKU#0915222047-1', name: '户外钛餐具套装', quantity: 2, price: 1245.00 },
        ],
        shipping_address: {
          city: 'Новосибирск',
          region: 'Новосибирская область',
          postal_code: '630000',
        },
      },
    ];
    setOrders(mockData);
    setFilteredOrders(mockData);
  }, []);

  useEffect(() => {
    let filtered = orders;
    if (searchText) {
      filtered = filtered.filter(o => 
        o.order_number.toLowerCase().includes(searchText.toLowerCase()) ||
        o.customer_name.toLowerCase().includes(searchText.toLowerCase())
      );
    }
    if (statusFilter !== 'all') {
      filtered = filtered.filter(o => o.fulfillment_status === statusFilter);
    }
    if (activeTab !== 'all') {
      filtered = filtered.filter(o => o.status === activeTab);
    }
    setFilteredOrders(filtered);
  }, [searchText, statusFilter, activeTab, orders]);

  const getStatusTag = (status: string, type: string) => {
    if (type === 'fulfillment') {
      const statusMap: Record<string, { color: string; text: string }> = {
        awaiting_shipment: { color: 'orange', text: '待发货' },
        awaiting_delivery: { color: 'blue', text: '待收货' },
        delivered: { color: 'green', text: '已送达' },
        cancelled: { color: 'red', text: '已取消' },
      };
      return <Tag color={statusMap[status]?.color || 'default'}>{statusMap[status]?.text || status}</Tag>;
    }
    const statusMap: Record<string, { color: string; text: string }> = {
      pending: { color: 'default', text: '待支付' },
      processing: { color: 'processing', text: '处理中' },
      completed: { color: 'green', text: '已完成' },
      cancelled: { color: 'red', text: '已取消' },
    };
    return <Tag color={statusMap[status]?.color || 'default'}>{statusMap[status]?.text || status}</Tag>;
  };

  const columns: ColumnsType<Order> = [
    {
      title: '订单号',
      dataIndex: 'order_number',
      key: 'order_number',
      width: 150,
    },
    {
      title: '客户',
      dataIndex: 'customer_name',
      key: 'customer_name',
      width: 150,
    },
    {
      title: '商品',
      dataIndex: 'products',
      key: 'products',
      width: 200,
      render: (products: Array<{ name: string; quantity: number }>) => (
        <span>
          {products.map((p, i) => (
            <div key={i}>{p.name} x{p.quantity}</div>
          ))}
        </span>
      ),
    },
    {
      title: '金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 100,
      render: (amount: number) => `₽${amount?.toFixed(2) || 0}`,
    },
    {
      title: '支付状态',
      dataIndex: 'payment_status',
      key: 'payment_status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'paid' ? 'green' : 'orange'}>
          {status === 'paid' ? '已支付' : '待支付'}
        </Tag>
      ),
    },
    {
      title: '配送状态',
      dataIndex: 'fulfillment_status',
      key: 'fulfillment_status',
      width: 100,
      render: (status: string) => getStatusTag(status, 'fulfillment'),
    },
    {
      title: '订单状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status, 'order'),
    },
    {
      title: '下单时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
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
  const completedCount = orders.filter(o => o.status === 'completed').length;
  const totalAmount = orders.reduce((sum, o) => sum + o.total_amount, 0);

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="订单总数" 
              value={orders.length} 
              prefix={<CarOutlined />} 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="待发货" 
              value={pendingCount} 
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="处理中" 
              value={processingCount} 
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="销售额" 
              value={totalAmount} 
              suffix="₽"
              prefix={<DollarOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card 
        title="订单列表"
        extra={
          <Space>
            <Search
              placeholder="搜索订单号或客户"
              onSearch={setSearchText}
              style={{ width: 200 }}
              allowClear
            />
            <Button icon={<SyncOutlined />}>同步订单</Button>
          </Space>
        }
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <Tabs.TabPane tab={`全部 (${orders.length})`} key="all" />
          <Tabs.TabPane tab={`待发货 (${pendingCount})`} key="pending" />
          <Tabs.TabPane tab={`处理中 (${processingCount})`} key="processing" />
          <Tabs.TabPane tab={`已完成 (${completedCount})`} key="completed" />
        </Tabs>

        <Table
          columns={columns}
          dataSource={filteredOrders}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      <Modal
        title="订单详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={700}
      >
        {selectedOrder && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="订单号" span={2}>
              {selectedOrder.order_number}
            </Descriptions.Item>
            <Descriptions.Item label="Ozon订单ID">
              {selectedOrder.platform_order_id}
            </Descriptions.Item>
            <Descriptions.Item label="客户">
              {selectedOrder.customer_name}
            </Descriptions.Item>
            <Descriptions.Item label="订单金额">
              ₽{selectedOrder.total_amount.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="支付状态">
              <Tag color={selectedOrder.payment_status === 'paid' ? 'green' : 'orange'}>
                {selectedOrder.payment_status === 'paid' ? '已支付' : '待支付'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="配送状态" span={2}>
              {getStatusTag(selectedOrder.fulfillment_status, 'fulfillment')}
            </Descriptions.Item>
            <Descriptions.Item label="收货城市">
              {selectedOrder.shipping_address.city}
            </Descriptions.Item>
            <Descriptions.Item label="邮编">
              {selectedOrder.shipping_address.postal_code}
            </Descriptions.Item>
            <Descriptions.Item label="下单时间" span={2}>
              {selectedOrder.created_at}
            </Descriptions.Item>
            <Descriptions.Item label="商品信息" span={2}>
              {selectedOrder.products.map((p, i) => (
                <div key={i}>
                  {p.sku} - {p.name} x{p.quantity} = ₽{p.price}
                </div>
              ))}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default OrdersPage;
