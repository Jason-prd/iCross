// -*- coding: utf-8 -*-
/**
 * 运营仪表盘
 * 展示店铺运营关键数据
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Progress, List, Typography, Space, Button } from 'antd';
import { 
  ShopOutlined, 
  ShoppingCartOutlined, 
  DollarOutlined, 
  RiseOutlined,
  StockOutlined,
  WarningOutlined,
  CarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { dashboardApi, DashboardStats } from '../services/api';

const { Title, Text } = Typography;

const DashboardNew: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [lowStockProducts, setLowStockProducts] = useState<any[]>([]);
  const [recentOrders, setRecentOrders] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // 并行请求
      const [statsData, lowStock, recent] = await Promise.all([
        dashboardApi.getStats().catch(() => null),
        dashboardApi.getLowStock(5).catch(() => []),
        dashboardApi.getRecentOrders(5).catch(() => []),
      ]);
      
      setStats(statsData);
      setLowStockProducts(lowStock);
      setRecentOrders(recent);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // 如果没有数据，使用模拟数据
  const data = stats || {
    selection_total: 59,
    selection_selected: 59,
    selection_pending: 6,
    selection_listed: 53,
    order_total: 156,
    order_pending: 12,
    order_processing: 8,
    order_completed: 136,
    order_total_amount: 245600,
    dropship_total: 45,
    dropship_pending: 3,
    dropship_shipped: 5,
    dropship_total_profit: 12850,
    product_total: 53,
    product_low_stock: 8,
    product_avg_profit_rate: 28.5,
  };

  const lowStock = lowStockProducts.length > 0 ? lowStockProducts : [
    { sku: 'SKU#0828104003-1', name: 'iPhone手机壳', stock: 5, threshold: 10 },
    { sku: 'SKU#0829000219-1', name: '合金车模', stock: 3, threshold: 10 },
    { sku: 'SKU#0915222047-1', name: '户外钛餐具', stock: 8, threshold: 10 },
    { sku: 'SKU#0917212854-1', name: '宠物衣服', stock: 2, threshold: 10 },
    { sku: 'SKU#0828103347-1', name: '手机支架', stock: 7, threshold: 10 },
  ];

  const recent = recentOrders.length > 0 ? recentOrders : [
    { order_number: '123456791', customer: 'Ivan P.', amount: 2490, status: 'pending', time: '10分钟前' },
    { order_number: '123456790', customer: 'Anna S.', amount: 1590, status: 'shipped', time: '30分钟前' },
    { order_number: '123456789', customer: 'Dmitry I.', amount: 899, status: 'delivered', time: '1小时前' },
    { order_number: '123456788', customer: 'Maria K.', amount: 1890, status: 'delivered', time: '2小时前' },
    { order_number: '123456787', customer: 'Alexey M.', amount: 3290, status: 'delivered', time: '3小时前' },
  ];

  const getStatusTag = (status: string) => {
    const map: Record<string, { color: string; text: string }> = {
      pending: { color: 'orange', text: '待发货' },
      shipped: { color: 'blue', text: '已发货' },
      delivered: { color: 'green', text: '已送达' },
    };
    return <Tag color={map[status]?.color || 'default'}>{map[status]?.text || status}</Tag>;
  };

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>运营仪表盘</Title>
        <Button icon={<SyncOutlined />} onClick={loadData} loading={loading}>刷新数据</Button>
      </div>

      {/* 核心指标 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Ozon商品数"
              value={data.selection_listed}
              suffix={`/ ${data.selection_total}`}
              prefix={<ShopOutlined />}
            />
            <Text type="secondary">已上架 / 总选品</Text>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本月订单"
              value={data.order_total}
              prefix={<ShoppingCartOutlined />}
            />
            <Text type="secondary">销售额: ₽{data.order_total_amount.toLocaleString()}</Text>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="代发利润"
              value={data.dropship_total_profit}
              suffix="¥"
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Text type="secondary">已完成 {data.dropship_total} 单</Text>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均利润率"
              value={data.product_avg_profit_rate}
              suffix="%"
              prefix={<RiseOutlined />}
            />
            <Text type="secondary">商品数: {data.product_total}</Text>
          </Card>
        </Col>
      </Row>

      {/* 订单和选品状态 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="订单概览">
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="待发货"
                  value={data.order_pending}
                  valueStyle={{ color: '#faad14' }}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="处理中"
                  value={data.order_processing}
                  valueStyle={{ color: '#1890ff' }}
                  prefix={<SyncOutlined spin />}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="已完成"
                  value={data.order_completed}
                  valueStyle={{ color: '#52c41a' }}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <Text>完成率: </Text>
              <Progress 
                percent={Math.round(data.order_completed / data.order_total * 100) || 0} 
                strokeColor="#52c41a"
                style={{ width: '80%' }}
              />
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="选品状态">
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="已选品"
                  value={data.selection_selected}
                  prefix={<ShoppingCartOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="待上架"
                  value={data.selection_pending}
                  valueStyle={{ color: '#faad14' }}
                  prefix={<ClockCircleOutlined />}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="已上架"
                  value={data.selection_listed}
                  valueStyle={{ color: '#52c41a' }}
                  prefix={<ShopOutlined />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <Text>上架率: </Text>
              <Progress 
                percent={Math.round(data.selection_listed / data.selection_selected * 100) || 0} 
                strokeColor="#52c41a"
                style={{ width: '80%' }}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* 低库存和最近订单 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card 
            title={
              <Space>
                <WarningOutlined style={{ color: '#ff4d4f' }} />
                低库存预警
              </Space>
            }
            extra={<Tag color="red">{data.product_low_stock} 个</Tag>}
          >
            <List
              size="small"
              dataSource={lowStock}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.sku}
                    description={item.name}
                  />
                  <Space>
                    <Text type="danger">{item.stock}</Text>
                    <Text type="secondary">/ {item.threshold}</Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card 
            title="最近订单"
            extra={<Button type="link" href="/orders/new">查看全部</Button>}
          >
            <List
              size="small"
              dataSource={recent}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.order_number}
                    description={
                      <Space>
                        <Text>{item.customer}</Text>
                        <Text type="secondary">{item.time}</Text>
                      </Space>
                    }
                  />
                  <Space>
                    <Text>₽{item.amount}</Text>
                    {getStatusTag(item.status)}
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* 代发概览 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="代发订单概览">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="代发订单总数"
                  value={data.dropship_total}
                  prefix={<CarOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="待处理"
                  value={data.dropship_pending}
                  valueStyle={{ color: '#faad14' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="已发货"
                  value={data.dropship_shipped}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="总利润"
                  value={data.dropship_total_profit}
                  suffix="¥"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardNew;
