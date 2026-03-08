// -*- coding: utf-8 -*-
/**
 * 选品管理页面
 * 显示所有已选商品
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Space, Input, Select, Modal, Descriptions, Row, Col, Statistic } from 'antd';
import { EyeOutlined, ShoppingOutlined, SearchOutlined, FilterOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Search } = Input;

interface SelectionProduct {
  id: string;
  master_sku: string;
  title: string;
  selection_status: string;
  listing_status: string;
  source_url: string;
  source_price: number;
  source_supplier: string;
  category: string;
  created_at: string;
}

const SelectionProducts: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<SelectionProduct[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<SelectionProduct[]>([]);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedProduct, setSelectedProduct] = useState<SelectionProduct | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  // 模拟数据
  useEffect(() => {
    const mockData: SelectionProduct[] = [
      {
        id: '1',
        master_sku: 'SKU#0828104003',
        title: '跨境爆款复古蝴蝶保护壳轻奢适用iPhone17Promax潮牌苹果16手机壳',
        selection_status: 'selected',
        listing_status: 'listed',
        source_url: 'https://detail.1688.com/offer/123456789.html',
        source_price: 16.00,
        source_supplier: '深圳代发商',
        category: '手机配件',
        created_at: '2026-02-27',
      },
      {
        id: '2',
        master_sku: 'SKU#0829000219',
        title: 'Postercars合金车模1:64超级跑车赛车玩具车模滑行收藏摆件挂卡',
        selection_status: 'selected',
        listing_status: 'not_listed',
        source_url: 'https://detail.1688.com/offer/234567890.html',
        source_price: 69.00,
        source_supplier: '上海代发商',
        category: '玩具',
        created_at: '2026-02-27',
      },
      {
        id: '3',
        master_sku: 'SKU#0915222047',
        title: '纯钛户外套锅煎锅野炊露营组合餐具可折叠轻量便携汤锅煎煮',
        selection_status: 'selected',
        listing_status: 'pending',
        source_url: 'https://detail.1688.com/offer/345678901.html',
        source_price: 49.00,
        source_supplier: '广州代发商',
        category: '户外用品',
        created_at: '2026-02-27',
      },
    ];
    setProducts(mockData);
    setFilteredProducts(mockData);
  }, []);

  // 搜索过滤
  useEffect(() => {
    let filtered = products;
    if (searchText) {
      filtered = filtered.filter(p => 
        p.master_sku.toLowerCase().includes(searchText.toLowerCase()) ||
        p.title.toLowerCase().includes(searchText.toLowerCase())
      );
    }
    if (statusFilter !== 'all') {
      filtered = filtered.filter(p => p.listing_status === statusFilter);
    }
    setFilteredProducts(filtered);
  }, [searchText, statusFilter, products]);

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      draft: { color: 'default', text: '未选品' },
      selected: { color: 'blue', text: '已选品' },
      not_listed: { color: 'default', text: '未上架' },
      pending: { color: 'orange', text: '待上架' },
      listing: { color: 'processing', text: '上架中' },
      listed: { color: 'green', text: '已上架' },
    };
    const s = statusMap[status] || { color: 'default', text: status };
    return <Tag color={s.color}>{s.text}</Tag>;
  };

  const columns: ColumnsType<SelectionProduct> = [
    {
      title: 'SPU',
      dataIndex: 'master_sku',
      key: 'master_sku',
      width: 180,
      fixed: 'left',
    },
    {
      title: '商品名称',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 300,
    },
    {
      title: '选品状态',
      dataIndex: 'selection_status',
      key: 'selection_status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '上架状态',
      dataIndex: 'listing_status',
      key: 'listing_status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '采购价(¥)',
      dataIndex: 'source_price',
      key: 'source_price',
      width: 100,
      render: (price: number) => `¥${price?.toFixed(2) || 0}`,
    },
    {
      title: '供应商',
      dataIndex: 'source_supplier',
      key: 'source_supplier',
      width: 120,
    },
    {
      title: '类目',
      dataIndex: 'category',
      key: 'category',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedProduct(record);
              setDetailVisible(true);
            }}
          >
            详情
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已选品总数" 
              value={products.length} 
              prefix={<ShoppingOutlined />} 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="待上架" 
              value={products.filter(p => p.listing_status === 'pending').length} 
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="已上架" 
              value={products.filter(p => p.listing_status === 'listed').length} 
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="未上架" 
              value={products.filter(p => p.listing_status === 'not_listed').length} 
            />
          </Card>
        </Col>
      </Row>

      <Card 
        title="选品管理" 
        extra={
          <Space>
            <Search
              placeholder="搜索SPU或商品名称"
              onSearch={setSearchText}
              style={{ width: 250 }}
              allowClear
            />
            <Select
              placeholder="上架状态"
              style={{ width: 120 }}
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { value: 'all', label: '全部' },
                { value: 'not_listed', label: '未上架' },
                { value: 'pending', label: '待上架' },
                { value: 'listed', label: '已上架' },
              ]}
            />
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={filteredProducts}
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
        title="商品选品详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={700}
      >
        {selectedProduct && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="SPU" span={2}>
              {selectedProduct.master_sku}
            </Descriptions.Item>
            <Descriptions.Item label="商品名称" span={2}>
              {selectedProduct.title}
            </Descriptions.Item>
            <Descriptions.Item label="选品状态">
              {getStatusTag(selectedProduct.selection_status)}
            </Descriptions.Item>
            <Descriptions.Item label="上架状态">
              {getStatusTag(selectedProduct.listing_status)}
            </Descriptions.Item>
            <Descriptions.Item label="采购价">
              ¥{selectedProduct.source_price?.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="供应商">
              {selectedProduct.source_supplier}
            </Descriptions.Item>
            <Descriptions.Item label="1688链接" span={2}>
              <a href={selectedProduct.source_url} target="_blank" rel="noopener noreferrer">
                {selectedProduct.source_url}
              </a>
            </Descriptions.Item>
            <Descriptions.Item label="类目">
              {selectedProduct.category}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {selectedProduct.created_at}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default SelectionProducts;
