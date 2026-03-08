// -*- coding: utf-8 -*-
/**
 * Ozon商品页面 - Tab标签页版本
 * - Tab1: 基础信息 (offer_id, name, 尺寸重量, 价格)
 * - Tab2: 商品图片 (images, primary_image, color_image)
 * - Tab3: 商品属性 (attributes)
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Space, Input, Row, Col, Statistic, Modal, Descriptions, Tooltip, Form, InputNumber, Select, message, Spin, Divider, Checkbox, Tabs, List, Empty } from 'antd';
import { EyeOutlined, EditOutlined, SyncOutlined, DollarOutlined, StockOutlined, ShopOutlined, ReloadOutlined, DeleteOutlined, PlusOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { ozonApi } from '../services/api';

const { Search } = Input;

interface AttributeOption { value_id: number; value: string; info?: string; picture?: string; }
interface ProductAttribute { attribute_id: number; name?: string; attribute_name?: string; type?: string; attribute_type?: string; dictionary_id?: number; group_id?: number; group_name?: string; is_required?: boolean; is_collection?: boolean; max_value_count?: number; value?: string; value_id?: number | string; values?: AttributeOption[]; }

interface OzonProduct {
  id: string; sku: string; spu: string; title: string; ozon_price: number; ozon_stock: number; ozon_product_id: string;
  platform_status: string; listing_status: string; profit_rate: number; sales_30d: number; last_synced: string;
  source_price?: number; source_supplier?: string; category_id?: number; category_name?: string; type_id?: number; attributes?: ProductAttribute[];
  depth?: number; width?: number; height?: number; dimension_unit?: string; weight?: number; weight_unit?: string;
  old_price?: string; vat?: string; currency_code?: string; barcode?: string; images?: string[]; primary_image?: string; color_image?: string;
}

const OzonProductsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<OzonProduct[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<OzonProduct[]>([]);
  const [searchText, setSearchText] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<OzonProduct | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [editVisible, setEditVisible] = useState(false);
  const [editingProduct, setEditingProduct] = useState<OzonProduct | null>(null);
  const [editForm] = Form.useForm();
  const [activeTab, setActiveTab] = useState('basic');
  const [categoryAttributes, setCategoryAttributes] = useState<ProductAttribute[]>([]);
  const [attributesLoading, setAttributesLoading] = useState(false);
  const [editingAttributes, setEditingAttributes] = useState<Record<number, number | number[]>>({});
  const [editingImages, setEditingImages] = useState<string[]>([]);
  const [primaryImage, setPrimaryImage] = useState('');
  const [colorImage, setColorImage] = useState('');

  useEffect(() => {
    const mockData: OzonProduct[] = [
      { id: '1', sku: 'SKU#0828104003-1', spu: 'SKU#0828104003', title: '跨境爆款复古蝴蝶保护壳轻奢适用iPhone17Promax潮牌苹果16手机壳', ozon_price: 899.00, ozon_stock: 100, ozon_product_id: '1803722916', platform_status: 'active', listing_status: 'listed', profit_rate: 35.5, sales_30d: 15, last_synced: '2026-02-27 21:00', source_price: 16.00, source_supplier: '深圳代发商', category_id: 17032965, category_name: '手机壳', type_id: 17032965, depth: 10, width: 80, height: 150, dimension_unit: 'mm', weight: 50, weight_unit: 'g', price: '899.00', old_price: '1299.00', vat: '0.10', currency_code: 'RUB', barcode: '1234567890123', images: ['https://via.placeholder.com/800x800/FF6B6B/FFFFFF?text=Product+Image+1', 'https://via.placeholder.com/800x800/4ECDC4/FFFFFF?text=Product+Image+2'], primary_image: 'https://via.placeholder.com/800x800/FF6B6B/FFFFFF?text=Product+Image+1' },
      { id: '2', sku: 'SKU#0828104003-2', spu: 'SKU#0828104003', title: '跨境爆款复古蝴蝶保护壳轻奢适用iPhone17Promax潮牌苹果16手机壳', ozon_price: 899.00, ozon_stock: 50, ozon_product_id: '1803722916', platform_status: 'active', listing_status: 'listed', profit_rate: 35.5, sales_30d: 8, last_synced: '2026-02-27 21:00', source_price: 18.00, source_supplier: '深圳代发商', category_id: 17032965, category_name: '手机壳', type_id: 17032965 },
      { id: '3', sku: 'SKU#0829000219-1', spu: 'SKU#0829000219', title: 'Postercars合金车模1:64超级跑车赛车玩具车模滑行收藏摆件挂卡', ozon_price: 1590.00, ozon_stock: 20, ozon_product_id: '1822804783', platform_status: 'active', listing_status: 'listed', profit_rate: 28.0, sales_30d: 3, last_synced: '2026-02-27 21:00', source_price: 69.00, source_supplier: '上海代发商' },
    ];
    setProducts(mockData);
    setFilteredProducts(mockData);
  }, []);

  useEffect(() => {
    setFilteredProducts(searchText ? products.filter(p => p.sku.toLowerCase().includes(searchText.toLowerCase()) || p.title.toLowerCase().includes(searchText.toLowerCase())) : products);
  }, [searchText, products]);

  const getStatusTag = (status: string) => {
    const map = { active: { color: 'green', text: '在售' }, inactive: { color: 'default', text: '下架' }, archived: { color: 'red', text: '归档' } };
    const s = map[status] || { color: 'default', text: status };
    return <Tag color={s.color}>{s.text}</Tag>;
  };
  const getProfitTag = (rate: number) => rate >= 30 ? <Tag color="green">高利润 {rate}%</Tag> : rate >= 15 ? <Tag color="orange">中等 {rate}%</Tag> : <Tag color="red">低利润 {rate}%</Tag>;

  const handleEdit = async (record: OzonProduct) => {
    setEditingProduct(record);
    setActiveTab('basic');
    editForm.setFieldsValue({ ozon_price: record.ozon_price, ozon_stock: record.ozon_stock, name: record.title, offer_id: record.sku, depth: record.depth, width: record.width, height: record.height, dimension_unit: record.dimension_unit || 'mm', weight: record.weight, weight_unit: record.weight_unit || 'g', price: record.price || String(record.ozon_price), old_price: record.old_price, vat: record.vat || '0.10', currency_code: record.currency_code || 'RUB', barcode: record.barcode });
    setEditingImages(record.images || []);
    setPrimaryImage(record.primary_image || '');
    setColorImage(record.color_image || '');
    if (record.category_id && record.type_id) { loadCategoryAttributes(record.category_id, record.type_id, record.attributes); }
    else { setCategoryAttributes([]); setEditingAttributes({}); }
    setEditVisible(true);
  };

  const loadCategoryAttributes = async (categoryId: number, typeId: number, existingAttrs?: ProductAttribute[]) => {
    setAttributesLoading(true);
    try {
      const attrs = await ozonApi.getDescriptionCategoryAttribute({ description_category_id: categoryId, type_id: typeId });
      const attrsWithOptions: ProductAttribute[] = await Promise.all((attrs as any[]).map(async (attr: any) => {
        const attributeType = attr.type || attr.attribute_type;
        const dictionaryId = attr.dictionary_id;
        const isCollection = attr.is_collection || (attr.max_value_count && attr.max_value_count > 1);
        let options: AttributeOption[] = [];
        if (dictionaryId && dictionaryId > 0) {
          try {
            const values = await ozonApi.getDescriptionCategoryAttributeValues({ description_category_id: categoryId, type_id: typeId, attribute_id: attr.attribute_id });
            options = (values as any[]).map((v: any) => ({ value_id: v.value_id, value: v.value, info: v.info, picture: v.picture }));
          } catch (e) { console.error('Failed to load values for attribute ' + attr.attribute_id + ':', e); }
        }
        return { attribute_id: attr.attribute_id, name: attr.name, attribute_name: attr.attribute_name || attr.name, type: attributeType, attribute_type: attributeType, dictionary_id: dictionaryId, group_id: attr.group_id, group_name: attr.group_name, is_required: attr.is_required, is_collection: isCollection, max_value_count: attr.max_value_count, values: options };
      }));
      setCategoryAttributes(attrsWithOptions);
      if (existingAttrs) {
        const initialSelected: Record<number, number | number[]> = {};
        existingAttrs.forEach((attr: ProductAttribute) => {
          if (attr.value_id) {
            if (attr.is_collection || (attr.max_value_count && attr.max_value_count > 1)) { const ids = String(attr.value_id).split(',').map(Number); initialSelected[attr.attribute_id] = ids; }
            else { initialSelected[attr.attribute_id] = attr.value_id as number; }
          }
        });
        setEditingAttributes(initialSelected as Record<number, number | number[]>);
      } else { setEditingAttributes({}); }
    } catch (error) { console.error('Failed to load category attributes:', error); message.warning('加载属性选项失败，请稍后重试'); setCategoryAttributes([]); }
    finally { setAttributesLoading(false); }
  };

  const handleAttributeChange = (attributeId: number, value: number | number[]) => setEditingAttributes(prev => ({ ...prev, [attributeId]: value }));
  const handleAddImage = (url: string) => { if (url && editingImages.length < 30) setEditingImages([...editingImages, url]); };
  const handleRemoveImage = (index: number) => { const newImages = [...editingImages]; newImages.splice(index, 1); setEditingImages(newImages); };
  const handleMoveImage = (index: number, direction: 'up' | 'down') => {
    const newImages = [...editingImages];
    if (direction === 'up' && index > 0) { [newImages[index], newImages[index - 1]] = [newImages[index - 1], newImages[index]]; }
    else if (direction === 'down' && index < newImages.length - 1) { [newImages[index], newImages[index + 1]] = [newImages[index + 1], newImages[index]]; }
    setEditingImages(newImages);
  };

  const handleSaveEdit = async () => {
    try {
      const values = await editForm.validateFields();
      const updatedAttributes: ProductAttribute[] = Object.entries(editingAttributes).filter(([_, value]) => value).map(([attrId, value]) => {
        const attr = categoryAttributes.find(a => a.attribute_id === Number(attrId));
        const isMultiSelect = attr?.is_collection || (attr?.max_value_count && attr?.max_value_count > 1);
        let valueId: number | string; let valueText: string;
        if (isMultiSelect && Array.isArray(value)) { valueId = value.join(','); const texts = value.map(vid => attr?.values?.find(v => v.value_id === vid)?.value).filter(Boolean); valueText = texts.join(', '); }
        else if (typeof value === 'number') { valueId = value; valueText = attr?.values?.find(v => v.value_id === value)?.value || ''; }
        else { valueId = 0; valueText = String(value); }
        return { attribute_id: Number(attrId), attribute_name: attr?.attribute_name || attr?.name || '', attribute_type: attr?.attribute_type || attr?.type || '', dictionary_id: attr?.dictionary_id, group_name: attr?.group_name, is_required: attr?.is_required, is_collection: attr?.is_collection, max_value_count: attr?.max_value_count, value_id: valueId, value: valueText };
      });
      const updatedProducts = products.map(p => {
        if (p.id === editingProduct?.id) {
          const sourcePrice = p.source_price || 0; const newPrice = values.ozon_price; const cost = sourcePrice * 13 * 1.2; const newProfitRate = ((newPrice - cost) / newPrice) * 100;
          return { ...p, ozon_price: values.ozon_price, ozon_stock: values.ozon_stock, profit_rate: newProfitRate, title: values.name, depth: values.depth, width: values.width, height: values.height, dimension_unit: values.dimension_unit, weight: values.weight, weight_unit: values.weight_unit, price: values.price, old_price: values.old_price, vat: values.vat, currency_code: values.currency_code, barcode: values.barcode, images: editingImages, primary_image: primaryImage || editingImages[0], color_image: colorImage, attributes: updatedAttributes };
        }
        return p;
      });
      setProducts(updatedProducts); setFilteredProducts(updatedProducts); message.success('商品信息已更新'); setEditVisible(false);
    } catch (error) { console.error('Failed to save:', error); }
  };

  const renderBasicInfoTab = () => (
    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
      <Form form={editForm} layout="vertical">
        <Divider orientation="left">基本信息</Divider>
        <Row gutter={16}>
          <Col span={12}><Form.Item label="SKU" name="offer_id"><Input disabled /></Form.Item></Col>
          <Col span={12}><Form.Item label="类目ID" name="description_category_id"><InputNumber style={{ width: '100%' }} disabled={!!editingProduct?.category_id} /></Form.Item></Col>
        </Row>
        <Form.Item label="商品名称" name="name" rules={[{ required: true, message: '请输入商品名称' }]}><Input placeholder="请输入商品名称（最大500字符）" maxLength={500} /></Form.Item>
        <Form.Item label="条码" name="barcode"><Input placeholder="请输入商品条码" /></Form.Item>
        <Divider orientation="left">尺寸重量</Divider>
        <p style={{ fontSize: 12, color: '#999', marginBottom: 16 }}>注意：尺寸和重量为必填项，且不能为0</p>
        <Row gutter={16}>
          <Col span={6}><Form.Item label="深度" name="depth" rules={[{ required: true, message: '必填' }]}><InputNumber style={{ width: '100%' }} min={1} placeholder="depth" /></Form.Item></Col>
          <Col span={6}><Form.Item label="宽度" name="width" rules={[{ required: true, message: '必填' }]}><InputNumber style={{ width: '100%' }} min={1} placeholder="width" /></Form.Item></Col>
          <Col span={6}><Form.Item label="高度" name="height" rules={[{ required: true, message: '必填' }]}><InputNumber style={{ width: '100%' }} min={1} placeholder="height" /></Form.Item></Col>
          <Col span={6}><Form.Item label="单位" name="dimension_unit"><Select><Select.Option value="mm">mm (毫米)</Select.Option><Select.Option value="cm">cm (厘米)</Select.Option><Select.Option value="in">in (英寸)</Select.Option></Select></Form.Item></Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}><Form.Item label="重量" name="weight" rules={[{ required: true, message: '必填' }]}><InputNumber style={{ width: '100%' }} min={1} placeholder="weight" /></Form.Item></Col>
          <Col span={12}><Form.Item label="重量单位" name="weight_unit"><Select><Select.Option value="g">g (克)</Select.Option><Select.Option value="kg">kg (千克)</Select.Option><Select.Option value="lb">lb (磅)</Select.Option></Select></Form.Item></Col>
        </Row>
        <Divider orientation="left">价格设置</Divider>
        <Row gutter={16}>
          <Col span={8}><Form.Item label="售价 (RUB)" name="price" rules={[{ required: true, message: '必填' }]}><InputNumber style={{ width: '100%' }} min={0} step={10} placeholder="现价" /></Form.Item></Col>
          <Col span={8}><Form.Item label="原价 (RUB)" name="old_price"><InputNumber style={{ width: '100%' }} min={0} step={10} placeholder="划线价" /></Form.Item></Col>
          <Col span={8}><Form.Item label="增值税" name="vat"><Select><Select.Option value="0">0% (免VAT)</Select.Option><Select.Option value="0.05">5%</Select.Option><Select.Option value="0.07">7%</Select.Option><Select.Option value="0.10">10%</Select.Option><Select.Option value="0.20">20%</Select.Option></Select></Form.Item></Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}><Form.Item label="货币" name="currency_code"><Select><Select.Option value="RUB">RUB (卢布)</Select.Option><Select.Option value="CNY">CNY (人民币)</Select.Option><Select.Option value="USD">USD (美元)</Select.Option><Select.Option value="EUR">EUR (欧元)</Select.Option></Select></Form.Item></Col>
          <Col span={12}><Form.Item label="Ozon库存" name="ozon_stock" rules={[{ required: true, message: '必填' }]}><InputNumber style={{ width: '100%' }} min={0} placeholder="库存数量" /></Form.Item></Col>
        </Row>
      </Form>
    </div>
  );

  const renderImagesTab = () => (
    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
      <Divider orientation="left">主图设置</Divider>
      <Form layout="vertical">
        <Form.Item label="主图URL (primary_image)"><Input placeholder="请输入主图URL" value={primaryImage} onChange={e => setPrimaryImage(e.target.value)} addonAfter={<Button type="link" size="small" onClick={() => primaryImage && setEditingImages([primaryImage, ...editingImages.filter(img => img !== primaryImage)])} disabled={!primaryImage}>设为第一张</Button>} /></Form.Item>
        <Form.Item label="营销色图URL (color_image)"><Input placeholder="请输入营销色图URL" value={colorImage} onChange={e => setColorImage(e.target.value)} /></Form.Item>
        <Divider orientation="left">商品图片列表</Divider>
        <p style={{ fontSize: 12, color: '#999', marginBottom: 16 }}>最多30张图片，第一张将作为主图显示</p>
        <Form.Item label="添加图片URL">
          <Space.Compact style={{ width: '100%' }}>
            <Input placeholder="输入图片URL" id="newImageUrl" onPressEnter={(e) => { const v = (e.target as HTMLInputElement).value; if (v) { handleAddImage(v); (e.target as HTMLInputElement).value = ''; } }} />
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { const input = document.getElementById('newImageUrl') as HTMLInputElement; if (input?.value) { handleAddImage(input.value); input.value = ''; } }}>添加</Button>
          </Space.Compact>
        </Form.Item>
        {editingImages.length > 0 ? (
          <List size="small" dataSource={editingImages} renderItem={(url, index) => (
            <List.Item actions={[<Button key="up" type="text" icon={<ArrowUpOutlined />} onClick={() => handleMoveImage(index, 'up')} disabled={index === 0} />, <Button key="down" type="text" icon={<ArrowDownOutlined />} onClick={() => handleMoveImage(index, 'down')} disabled={index === editingImages.length - 1} />, <Button key="delete" type="text" danger icon={<DeleteOutlined />} onClick={() => handleRemoveImage(index)} />]}>
              <List.Item.Meta avatar={<div style={{ width: 50, height: 50, overflow: 'hidden', borderRadius: 4 }}><img src={url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} /></div>} title={'图片 ' + (index + 1) + (url === primaryImage || (!primaryImage && index === 0) ? ' (主图)' : '')} description={<span style={{ fontSize: 11, color: '#999' }}>{url.substring(0, 50)}...</span>} />
            </List.Item>
          )} />
        ) : (<Empty description="暂无图片，请添加图片URL" />)}
        <div style={{ marginTop: 16, fontSize: 12, color: '#999' }}>已添加 {editingImages.length}/30 张图片</div>
      </Form>
    </div>
  );

  const renderAttributesTab = () => (
    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
      {editingProduct?.category_id && editingProduct?.type_id ? (
        <Spin spinning={attributesLoading}>
          {categoryAttributes.length > 0 ? (
            <>
              {(() => { const groups: Record<string, ProductAttribute[]> = {}; categoryAttributes.forEach(attr => { const gn = attr.group_name || '其他属性'; if (!groups[gn]) groups[gn] = []; groups[gn].push(attr); }); return Object.entries(groups).map(([gn, attrs]) => (
                <div key={gn} style={{ marginBottom: 24 }}>{Object.keys(groups).length > 1 && <Divider orientation="left" style={{ fontWeight: 'bold', color: '#1890ff' }}>{gn}</Divider>}
                {attrs.map(attr => { const at = attr.type || attr.attribute_type; const hasDict = attr.dictionary_id && attr.dictionary_id > 0; const isMulti = attr.is_collection || (attr.max_value_count && attr.max_value_count > 1);
                  const renderCtrl = () => { if (!hasDict) { if (at === 'Integer' || at === 'Decimal') return <InputNumber style={{ width: '100%' }} placeholder={'请输入' + attr.attribute_name} value={(editingAttributes[attr.attribute_id] as number) || undefined} onChange={v => handleAttributeChange(attr.attribute_id, v as number)} />; return <Input placeholder={'请输入' + attr.attribute_name} value={(editingAttributes[attr.attribute_id] as number) || undefined} onChange={e => handleAttributeChange(attr.attribute_id, e.target.value as any)} />; }
                    if (isMulti) { const sv = (editingAttributes[attr.attribute_id] as number[]) || []; return <Checkbox.Group value={sv} onChange={v => handleAttributeChange(attr.attribute_id, v as number[])} style={{ width: '100%' }}><div style={{ maxHeight: 200, overflowY: 'auto' }}>{attr.values?.map(o => <Checkbox key={o.value_id} value={o.value_id}>{o.picture && <img src={o.picture} alt="" style={{ width: 20, height: 20, marginRight: 4, verticalAlign: 'middle' }} />}{o.value}</Checkbox>)}</div></Checkbox.Group>; }
                    return <Select placeholder={'请选择' + attr.attribute_name} value={editingAttributes[attr.attribute_id] as number} onChange={v => handleAttributeChange(attr.attribute_id, v)} allowClear style={{ width: '100%' }} showSearch optionFilterProp="children">{attr.values?.map(o => <Select.Option key={o.value_id} value={o.value_id}>{o.picture && <img src={o.picture} alt="" style={{ width: 20, height: 20, marginRight: 8, verticalAlign: 'middle' }} />}{o.value}</Select.Option>)}</Select>;
                  };
                  return <Form.Item key={attr.attribute_id} label={attr.attribute_name} required={attr.is_required} style={{ marginBottom: 12 }}>{renderCtrl()}</Form.Item>;
                })}</div>
              )); })()}
              <div style={{ marginTop: 8 }}><Button type="link" icon={<ReloadOutlined />} onClick={() => editingProduct?.category_id && editingProduct?.type_id && loadCategoryAttributes(editingProduct.category_id, editingProduct.type_id, editingProduct.attributes)} size="small">刷新属性选项</Button></div>
            </>
          ) : <div style={{ textAlign: 'center', padding: 24, color: '#999' }}>{attributesLoading ? '加载中...' : '暂无属性'}</div>}
        </Spin>
      ) : <Empty description="该商品缺少分类信息，无法编辑属性" />}
    </div>
  );

  const columns: ColumnsType<OzonProduct> = [
    { title: 'SKU', dataIndex: 'sku', key: 'sku', width: 180 },
    { title: 'SPU', dataIndex: 'spu', key: 'spu', width: 150 },
    { title: '商品名称', dataIndex: 'title', key: 'title', ellipsis: true, width: 250 },
    { title: '采购价(¥)', dataIndex: 'source_price', key: 'source_price', width: 100, render: (p: number) => p ? '¥' + p.toFixed(2) : '-' },
    { title: 'Ozon售价(RUB)', dataIndex: 'ozon_price', key: 'ozon_price', width: 100, render: (p: number) => 'RUB ' + (p?.toFixed(2) || 0) },
    { title: '库存', dataIndex: 'ozon_stock', key: 'ozon_stock', width: 80, render: (s: number) => (<Tooltip title={s < 10 ? '库存不足' : ''}><span style={{ color: s < 10 ? '#ff4d4f' : undefined }}>{s}</span></Tooltip>) },
    { title: '利润率', dataIndex: 'profit_rate', key: 'profit_rate', width: 100, render: (r: number) => getProfitTag(r) },
    { title: '30天销量', dataIndex: 'sales_30d', key: 'sales_30d', width: 90 },
    { title: '状态', dataIndex: 'platform_status', key: 'platform_status', width: 80, render: (s: string) => getStatusTag(s) },
    { title: '操作', key: 'action', width: 120, render: (_, r) => (<Space><Button type="link" icon={<EyeOutlined />} onClick={() => { setSelectedProduct(r); setDetailVisible(true); }}>详情</Button><Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(r)}>编辑</Button></Space>) },
  ];

  const totalSales = products.reduce((s, p) => s + p.sales_30d, 0);
  const avgProfit = products.length > 0 ? products.reduce((s, p) => s + p.profit_rate, 0) / products.length : 0;
  const lowStock = products.filter(p => p.ozon_stock < 10).length;

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}><Card><Statistic title="Ozon商品总数" value={products.length} prefix={<ShopOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="30天总销量" value={totalSales} prefix={<StockOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="平均利润率" value={avgProfit.toFixed(1)} suffix="%" valueStyle={{ color: avgProfit >= 20 ? '#52c41a' : '#faad14' }} prefix={<DollarOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="低库存预警" value={lowStock} valueStyle={{ color: lowStock > 0 ? '#ff4d4f' : undefined }} /></Card></Col>
      </Row>
      <Card title="Ozon商品列表" extra={<Space><Search placeholder="搜索SKU或商品名称" onSearch={setSearchText} style={{ width: 250 }} allowClear /><Button icon={<SyncOutlined />}>同步Ozon</Button></Space>}>
        <Table columns={columns} dataSource={filteredProducts} rowKey="id" loading={loading} scroll={{ x: 1500 }} pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (t) => '共 ' + t + ' 条' }} />
      </Card>
      <Modal title="商品详情" open={detailVisible} onCancel={() => setDetailVisible(false)} footer={null} width={700}>
        {selectedProduct && (<Descriptions column={2} bordered size="small"><Descriptions.Item label="SKU" span={2}>{selectedProduct.sku}</Descriptions.Item><Descriptions.Item label="SPU" span={2}>{selectedProduct.spu}</Descriptions.Item><Descriptions.Item label="商品名称" span={2}>{selectedProduct.title}</Descriptions.Item><Descriptions.Item label="采购价">¥{selectedProduct.source_price?.toFixed(2)}</Descriptions.Item><Descriptions.Item label="供应商">{selectedProduct.source_supplier || '-'}</Descriptions.Item><Descriptions.Item label="Ozon商品ID">{selectedProduct.ozon_product_id}</Descriptions.Item><Descriptions.Item label="Ozon售价">RUB {selectedProduct.ozon_price?.toFixed(2)}</Descriptions.Item><Descriptions.Item label="库存">{selectedProduct.ozon_stock}</Descriptions.Item><Descriptions.Item label="状态">{getStatusTag(selectedProduct.platform_status)}</Descriptions.Item><Descriptions.Item label="利润率">{selectedProduct.profit_rate}%</Descriptions.Item><Descriptions.Item label="30天销量">{selectedProduct.sales_30d}</Descriptions.Item><Descriptions.Item label="最后同步" span={2}>{selectedProduct.last_synced}</Descriptions.Item></Descriptions>)}
      </Modal>
      <Modal title="编辑商品" open={editVisible} onCancel={() => setEditVisible(false)} onOk={handleSaveEdit} okText="保存" width={800}>
        {editingProduct && (<Tabs activeKey={activeTab} onChange={setActiveTab} items={[{ key: 'basic', label: '基础信息', children: renderBasicInfoTab() }, { key: 'images', label: '商品图片', children: renderImagesTab() }, { key: 'attributes', label: '商品属性', children: renderAttributesTab() }]} />)}
      </Modal>
    </div>
  );
};

export default OzonProductsPage;
