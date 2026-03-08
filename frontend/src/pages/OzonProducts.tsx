// -*- coding: utf-8 -*-
/**
 * Ozon商品页面
 * 显示所有已上架到Ozon的商品，支持编辑
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Space, Input, Row, Col, Statistic, Modal, Descriptions, Tooltip, Form, InputNumber, Select, message, Spin, Divider, Checkbox, Radio, Tabs, List, Switch, TreeSelect, Empty } from 'antd';
import { EyeOutlined, EditOutlined, SyncOutlined, DollarOutlined, StockOutlined, ShopOutlined, ReloadOutlined, ArrowUpOutlined, ArrowDownOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { ozonApi } from '../services/api';

const { Search } = Input;
const { TextArea } = Input;

// 属性选项接口 - 匹配Ozon API返回格式
interface AttributeOption {
  value_id: number;
  value: string;
  info?: string;
  picture?: string;
}

// 商品属性接口 - 匹配Ozon API返回格式
interface ProductAttribute {
  attribute_id: number;
  name?: string;  // 属性名称
  attribute_name?: string;
  type?: string;  // attribute_type: String, Integer, Decimal等
  attribute_type?: string;
  dictionary_id?: number;  // 字典ID >0 表示有选项
  group_id?: number;
  group_name?: string;  // 属性分组
  is_required?: boolean;
  is_collection?: boolean;  // 是否多选
  max_value_count?: number;  // 最大值数量
  // 当前已选的值
  value?: string;
  value_id?: number | string;  // 支持数字和逗号分隔的字符串（多选用）
  values?: AttributeOption[];  // 选项列表
}

interface OzonProduct {
  id: string;
  offer_id: string;
  sku?: string;
  spu?: string;
  title: string;
  ozon_price?: number;
  ozon_stock?: number;
  ozon_product_id?: number | string;
  platform_status?: string;
  listing_status?: string;
  profit_rate?: number;
  sales_30d?: number;
  last_synced?: string;
  primary_image?: string;
  images?: string[];
  // 分类和属性信息
  category_id?: number;
  category_name?: string;
  type_id?: number;
  attributes?: ProductAttribute[];
  // 选品信息
  source_price?: number;
  source_supplier?: string;
}

const OzonProductsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [products, setProducts] = useState<OzonProduct[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<OzonProduct[]>([]);
  const [searchText, setSearchText] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<OzonProduct | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [editVisible, setEditVisible] = useState(false);
  const [editingProduct, setEditingProduct] = useState<OzonProduct | null>(null);
  const [editForm] = Form.useForm();
  
  // Tab切换
  const [activeTab, setActiveTab] = useState("basic");
  
  // 类目相关
  const [categoryTreeData, setCategoryTreeData] = useState<any[]>([]);
  
  // 属性相关
  const [categoryAttributes, setCategoryAttributes] = useState<ProductAttribute[]>([]);
  const [attributesLoading, setAttributesLoading] = useState(false);
  const [editingAttributes, setEditingAttributes] = useState<Record<number, number | number[]>>({});
  // 延迟加载属性选项
  const [attributeValues, setAttributeValues] = useState<Record<number, any[]>>({});
  const [loadingAttributeValues, setLoadingAttributeValues] = useState<Set<number>>(new Set());
  
  // 图片相关
  const [editingImages, setEditingImages] = useState<string[]>([]);
  const [primaryImage, setPrimaryImage] = useState("");
  const [colorImage, setColorImage] = useState("");
  const [images360, setImages360] = useState<string[]>([]);

  // 加载商品列表
  const loadProducts = async () => {
    setLoading(true);
    try {
      const res = await ozonApi.getDbProducts({ limit: 100 });
      const items = (res.data?.items || res.data || []).map((item: any) => ({
        ...item,
        ozon_price: item.price,
        ozon_stock: item.stock,
        platform_status: item.status,
        listing_status: item.visibility,
      }));
      setProducts(items);
      setFilteredProducts(items);
    } catch (error) {
      console.error('加载商品失败:', error);
      message.error('加载商品失败');
    } finally {
      setLoading(false);
    }
  };

  // 同步Ozon商品
  const handleSync = async () => {
    setSyncing(true);
    try {
      await ozonApi.syncProducts();
      message.success('商品同步成功');
      await loadProducts();
    } catch (error) {
      console.error('同步失败:', error);
      message.error('同步失败');
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    if (searchText) {
      setFilteredProducts(products.filter(p => 
        p.sku.toLowerCase().includes(searchText.toLowerCase()) ||
        p.title.toLowerCase().includes(searchText.toLowerCase())
      ));
    } else {
      setFilteredProducts(products);
    }
  }, [searchText, products]);

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      active: { color: 'green', text: '在售' },
      inactive: { color: 'default', text: '下架' },
      archived: { color: 'red', text: '归档' },
    };
    const s = statusMap[status] || { color: 'default', text: status };
    return <Tag color={s.color}>{s.text}</Tag>;
  };

  const getProfitTag = (rate: number) => {
    if (rate >= 30) return <Tag color="green">高利润 {rate}%</Tag>;
    if (rate >= 15) return <Tag color="orange">中等 {rate}%</Tag>;
    return <Tag color="red">低利润 {rate}%</Tag>;
  };

  // 类目树转换 - 处理三级结构：一级(category_name) > 二级(category_name) > 三级(type_name)
  // 使用 description_category_id 或 type_id 作为 value，确保与商品数据匹配
  const convertToTreeData = (categories: any, parentPath: string = ''): any[] => {
    if (!Array.isArray(categories)) {
      console.warn("类目数据不是数组:", categories);
      return [];
    }
    return categories.map((cat: any) => {
      const title = cat.category_name || cat.type_name || cat.title;
      const currentPath = parentPath ? `${parentPath} > ${title}` : title;
      // 一级用description_category_id，二级用description_category_id，三级用type_id
      const value = cat.type_id || cat.description_category_id || cat.id;
      const children = cat.children && cat.children.length > 0 ? convertToTreeData(cat.children, currentPath) : undefined;
      return {
        value: value,
        label: currentPath,
        title: title,
        children: children,
        selectable: !!title,
        description_category_id: cat.description_category_id,
        type_id: cat.type_id,
        fullPath: currentPath,
      };
    });
  };

  // 加载类目树
  const loadCategoryTree = async () => {
    try {
      const result = await ozonApi.getAllCategoryTree();
      console.log("类目树API返回:", result);
      const data = result?.data || result;
      console.log("类型:", typeof data, Array.isArray(data));
      const treeData = convertToTreeData(data || []);
      console.log("转换后:", treeData);
      setCategoryTreeData(treeData);
    } catch (error) {
      console.error("加载类目树失败:", error);
    }
  };

  // 加载类目属性（只加载基本信息，不加载选项）
  const loadCategoryAttributes = async (categoryId: number, typeId: number) => {
    if (!categoryId || !typeId) { 
      console.warn("categoryId 或 typeId 无效，跳过加载属性");
      setCategoryAttributes([]);
      return; 
    }
    setAttributesLoading(true);
    setAttributeValues({});
    try {
      const result = await ozonApi.getDescriptionCategoryAttribute({
        description_category_id: categoryId,
        type_id: typeId,
      });
      const attrs = Array.isArray(result) ? result : (result.data || result.result || []);
      
      // 字段名映射：API返回的是id/name，前端需要attribute_id/attribute_name
      const mappedAttrs = attrs.map((attr: any) => ({
        ...attr,
        attribute_id: attr.id,
        attribute_name: attr.name,
        // 不在这里加载选项，延迟到用户点击时加载
      }));
      setCategoryAttributes(mappedAttrs);
    } catch (error) { 
      console.warn("加载属性失败 (已捕获):", error);
      setCategoryAttributes([]);
    }
    finally { setAttributesLoading(false); }
  };

  // 延迟加载单个属性的选项
  const loadAttributeValues = async (attr: any, categoryId: number, typeId: number) => {
    try {
      const attrId = attr.attribute_id;
      if (!attrId || attr.dictionary_id <= 0) return;
      if (attributeValues[attrId]?.length > 0) return; // 已加载
      if (loadingAttributeValues.has(attrId)) return; // 正在加载
      
      setLoadingAttributeValues(prev => new Set(prev).add(attrId));
      const result = await ozonApi.getDescriptionCategoryAttributeValues({
        description_category_id: categoryId,
        type_id: typeId,
        attribute_id: attrId,
      });
      console.log(`属性 ${attr.attribute_name} 选项返回:`, result);
      const values = result?.data || result || [];
      setAttributeValues(prev => ({
        ...prev,
        [attrId]: values,
      }));
    } catch (error) {
      console.warn(`加载属性选项失败:`, error);
    } finally {
      setLoadingAttributeValues(prev => {
        const next = new Set(prev);
        if (attr.attribute_id) next.delete(attr.attribute_id);
        return next;
      });
    }
  };

  // 初始化编辑数据
  const initEditData = async (product: any) => {
    setEditingImages(product.images || []);
    setPrimaryImage(product.primary_image || "");
    setColorImage(product.color_image || "");
    setImages360(product.images360 || []);
    setCategoryAttributes([]);
    setEditingAttributes({});
    setAttributeValues({});
    setLoadingAttributeValues(new Set());
    
    await loadCategoryTree();
    
    // 只有当 category_id 和 type_id 都存在时才加载属性
    if (product.category_id && product.type_id) {
      try {
        await loadCategoryAttributes(product.category_id, product.type_id);
      } catch (error) {
        console.warn("加载类目属性失败:", error);
      }
    }
    
    if (product.attributes && Array.isArray(product.attributes)) {
      const attrMap: Record<number, number | number[]> = {};
      (product.attributes || []).forEach((attr: any) => {
        if (attr.is_collection) {
          attrMap[attr.attribute_id] = String(attr.value_id || "").split(",").map(Number).filter(Boolean);
        } else {
          attrMap[attr.attribute_id] = Number(attr.value_id) || 0;
        }
      });
      setEditingAttributes(attrMap);
    }
  };

  // 图片处理函数
  const handleAddImage = (url: string) => { 
    if (url && editingImages.length < 30) setEditingImages([...editingImages, url]); 
  };
  const handleRemoveImage = (index: number) => { 
    const newImages = [...editingImages]; 
    newImages.splice(index, 1); 
    setEditingImages(newImages); 
  };
  const handleMoveImage = (index: number, direction: "up" | "down") => {
    const newImages = [...editingImages];
    if (direction === "up" && index > 0) {
      [newImages[index], newImages[index - 1]] = [newImages[index - 1], newImages[index]];
    } else if (direction === "down" && index < newImages.length - 1) {
      [newImages[index], newImages[index + 1]] = [newImages[index + 1], newImages[index]];
    }
    setEditingImages(newImages);
  };

  // 打开编辑弹窗
  const handleEdit = async (record: OzonProduct) => {
    setEditingProduct(record);
    setActiveTab("basic");
    setEditVisible(true);
    editForm.setFieldsValue({
      ozon_price: record.ozon_price,
      ozon_stock: record.ozon_stock,
    });
    try {
      await initEditData(record);
    } catch (error) {
      console.error("初始化编辑数据失败:", error);
    }
  };

  // 属性值变化 - 支持单选number和多选number[]
  const handleAttributeChange = (attributeId: number, value: number | number[]) => {
    setEditingAttributes(prev => ({
      ...prev,
      [attributeId]: value,
    }));
  };

  // 刷新属性选项 - 使用新的description-category API
  const refreshAttributes = async () => {
    if (!editingProduct?.category_id || !editingProduct?.type_id) return;
    
    setAttributesLoading(true);
    try {
      const attrs = await ozonApi.getDescriptionCategoryAttribute({
        description_category_id: editingProduct.category_id,
        type_id: editingProduct.type_id,
      });
      
      const attrsWithOptions: ProductAttribute[] = await Promise.all(
        (attrs as any[]).map(async (attr: any) => {
          const attributeType = attr.type || attr.attribute_type;
          const dictionaryId = attr.dictionary_id;
          const isCollection = attr.is_collection || (attr.max_value_count && attr.max_value_count > 1);
          
          let options: AttributeOption[] = [];
          if (dictionaryId && dictionaryId > 0) {
            try {
              const values = await ozonApi.getDescriptionCategoryAttributeValues({
                description_category_id: editingProduct.category_id!,
                type_id: editingProduct.type_id!,
                attribute_id: attr.attribute_id,
              });
              options = (values as any[]).map((v: any) => ({
                value_id: v.id,
                value: v.value,
                info: v.info,
                picture: v.picture,
              }));
            } catch (e) {
              console.error(`Failed to load values for attribute ${attr.attribute_id}:`, e);
            }
          }
          
          return {
            attribute_id: attr.attribute_id,
            name: attr.name,
            attribute_name: attr.attribute_name || attr.name,
            type: attributeType,
            attribute_type: attributeType,
            dictionary_id: dictionaryId,
            group_id: attr.group_id,
            group_name: attr.group_name,
            is_required: attr.is_required,
            is_collection: isCollection,
            max_value_count: attr.max_value_count,
            values: options,
          };
        })
      );
      
      setCategoryAttributes(attrsWithOptions);
      message.success('属性选项已刷新');
    } catch (error) {
      message.error('刷新属性失败');
    } finally {
      setAttributesLoading(false);
    }
  };

  // Tab 1: 基础信息
  const renderBasicInfoTab = () => (
    <div>
      <Descriptions column={1} bordered size="small">
        <Descriptions.Item label="SKU">{editingProduct?.offer_id || editingProduct?.sku || '-'}</Descriptions.Item>
        <Descriptions.Item label="商品名称">{editingProduct?.title || '-'}</Descriptions.Item>
      </Descriptions>
      
      <Form.Item 
        name="ozon_price" 
        label="Ozon售价 (₽)"
        rules={[{ required: true, message: '请输入售价' }]}
        style={{ marginTop: 16 }}
      >
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          step={10}
          placeholder="请输入Ozon售价"
          addonAfter="₽"
        />
      </Form.Item>
      
      <Form.Item 
        name="ozon_stock" 
        label="库存数量"
        rules={[{ required: true, message: '请输入库存' }]}
      >
        <InputNumber
          style={{ width: '100%' }}
          min={0}
          placeholder="请输入库存数量"
        />
      </Form.Item>

      <Form.Item label="商品类目">
        <Select
          showSearch
          allowClear
          placeholder="请搜索选择类目"
          style={{ width: '100%' }}
          value={editingProduct?.category_id}
          onChange={(value: number, option: any) => {
            setEditingProduct(prev => prev ? { 
              ...prev, 
              category_id: value,
              type_id: option?.type_id || value,
            } : null);
          }}
          filterOption={(input, option: any) => {
            const label = option?.label?.toLowerCase() || '';
            return label.includes(input.toLowerCase());
          }}
          options={categoryTreeData.reduce((acc: any[], cat) => {
            // 一级
            if (cat.label) {
              acc.push({ value: cat.value, label: cat.fullPath, type_id: cat.type_id, description_category_id: cat.description_category_id });
            }
            // 二级
            if (cat.children) {
              cat.children.forEach((child: any) => {
                if (child.label) {
                  acc.push({ value: child.value, label: child.fullPath, type_id: child.type_id, description_category_id: child.description_category_id });
                }
                // 三级
                if (child.children) {
                  child.children.forEach((grandchild: any) => {
                    if (grandchild.label) {
                      acc.push({ value: grandchild.value, label: grandchild.fullPath, type_id: grandchild.type_id, description_category_id: grandchild.description_category_id });
                    }
                  });
                }
              });
            }
            return acc;
          }, [])}
        />
      </Form.Item>
    </div>
  );

  // Tab 2: 图片
  const renderImagesTab = () => (
    <div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>主图</div>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="输入图片URL"
            value={primaryImage}
            onChange={(e) => setPrimaryImage(e.target.value)}
          />
          <Button icon={<PlusOutlined />} onClick={() => handleAddImage(primaryImage)}>添加</Button>
        </Space.Compact>
        {primaryImage && (
          <div style={{ marginTop: 8 }}>
            <img src={primaryImage} alt="主图" style={{ maxWidth: 150, maxHeight: 150, border: '1px solid #d9d9d9', borderRadius: 4 }} />
          </div>
        )}
      </div>

      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>图片列表 ({editingImages.length}/30)</div>
        <List
          size="small"
          dataSource={editingImages}
          renderItem={(img, index) => (
            <List.Item
              actions={[
                <Button key="up" type="text" icon={<ArrowUpOutlined />} size="small" onClick={() => handleMoveImage(index, "up")} disabled={index === 0} />,
                <Button key="down" type="text" icon={<ArrowDownOutlined />} size="small" onClick={() => handleMoveImage(index, "down")} disabled={index === editingImages.length - 1} />,
                <Button key="del" type="text" icon={<DeleteOutlined />} size="small" danger onClick={() => handleRemoveImage(index)} />,
              ]}
            >
              <List.Item.Meta
                avatar={<img src={img} alt="" style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 4 }} />}
                title={`图片 ${index + 1}`}
              />
            </List.Item>
          )}
          locale={{ emptyText: <Empty description="暂无图片" image={Empty.PRESENTED_IMAGE_SIMPLE} /> }}
        />
      </div>

      <div>
        <div style={{ marginBottom: 8, fontWeight: 500 }}>营销色图</div>
        <Input
          placeholder="输入营销色图URL"
          value={colorImage}
          onChange={(e) => setColorImage(e.target.value)}
          style={{ marginBottom: 8 }}
        />
        {colorImage && <img src={colorImage} alt="营销色图" style={{ maxWidth: 150, maxHeight: 150, border: '1px solid #d9d9d9', borderRadius: 4 }} />}
      </div>
    </div>
  );

  // Tab 3: 属性
  const renderAttributesTab = () => {
    if (!editingProduct?.category_id) {
      return <Empty description="请先选择类目" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    }
    
    return (
      <Spin spinning={attributesLoading}>
        {categoryAttributes.length > 0 ? (
          <div style={{ maxHeight: 500, overflowY: 'auto' }}>
            {(() => {
              const groups: Record<string, ProductAttribute[]> = {};
              categoryAttributes.forEach(attr => {
                const groupName = attr.group_name || '其他属性';
                if (!groups[groupName]) groups[groupName] = [];
                groups[groupName].push(attr);
              });
              
              return Object.entries(groups).map(([groupName, attrs]) => (
                <div key={groupName} style={{ marginBottom: 16 }}>
                  {Object.keys(groups).length > 1 && (
                    <div style={{ fontWeight: 'bold', marginBottom: 8, color: '#1890ff' }}>{groupName}</div>
                  )}
                  {attrs.map((attr) => {
                    const attributeType = attr.type || attr.attribute_type;
                    const hasDictionary = attr.dictionary_id && attr.dictionary_id > 0;
                    const isMultiSelect = attr.is_collection || (attr.max_value_count && attr.max_value_count > 1);
                    const values = Array.isArray(attributeValues[attr.attribute_id]) ? attributeValues[attr.attribute_id] : [];
                    const isValuesLoading = loadingAttributeValues.has(attr.attribute_id);
                    
                    const handleLoadValues = () => {
                      if (editingProduct?.category_id && editingProduct?.type_id) {
                        loadAttributeValues(attr, editingProduct.category_id, editingProduct.type_id);
                      }
                    };
                    
                    const renderControl = () => {
                      if (!hasDictionary) {
                        if (attributeType === 'Integer' || attributeType === 'Decimal') {
                          return (
                            <InputNumber
                              style={{ width: '100%' }}
                              placeholder={`请输入${attr.attribute_name}`}
                              value={(editingAttributes[attr.attribute_id] as number) || undefined}
                              onChange={(value) => handleAttributeChange(attr.attribute_id, value as number)}
                            />
                          );
                        }
                        return (
                          <Input
                            placeholder={`请输入${attr.attribute_name}`}
                            value={(editingAttributes[attr.attribute_id] as number) || undefined}
                            onChange={(e) => handleAttributeChange(attr.attribute_id, e.target.value as any)}
                          />
                        );
                      }
                      
                      if (isMultiSelect) {
                        const selectedValues = (editingAttributes[attr.attribute_id] as number[]) || [];
                        return (
                          <Spin spinning={isValuesLoading}>
                            <Checkbox.Group
                              value={selectedValues}
                              onChange={(vals) => handleAttributeChange(attr.attribute_id, vals as number[])}
                              style={{ width: '100%' }}
                            >
                              <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                                {values.map((option) => (
                                  <Checkbox key={option.id} value={option.id}>
                                    {option.picture && <img src={option.picture} alt="" style={{ width: 20, height: 20, marginRight: 4, verticalAlign: 'middle' }} />}
                                    {option.value}
                                  </Checkbox>
                                ))}
                              </div>
                            </Checkbox.Group>
                          </Spin>
                        );
                      }
                      
                      return (
                        <Select
                          placeholder={`请选择${attr.attribute_name}`}
                          value={editingAttributes[attr.attribute_id] as number}
                          onChange={(value) => handleAttributeChange(attr.attribute_id, value)}
                          onDropdownVisibleChange={(open) => { if (open && values.length === 0) handleLoadValues(); }}
                          allowClear
                          style={{ width: '100%' }}
                          showSearch
                          optionFilterProp="children"
                        >
                          {values.map((option) => (
                            <Select.Option key={option.id} value={option.id}>
                              {option.picture && <img src={option.picture} alt="" style={{ width: 20, height: 20, marginRight: 8, verticalAlign: 'middle' }} />}
                              {option.value}
                            </Select.Option>
                          ))}
                        </Select>
                      );
                    };
                    
                    return (
                      <Form.Item key={attr.attribute_id} label={attr.attribute_name} required={attr.is_required} style={{ marginBottom: 12 }}>
                        {renderControl()}
                      </Form.Item>
                    );
                  })}
                </div>
              ));
            })()}
            <Button type="link" icon={<ReloadOutlined />} onClick={refreshAttributes} size="small">刷新属性选项</Button>
          </div>
        ) : (
          <Empty description="暂无属性" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Spin>
    );
  };

  // 保存编辑
  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      const values = await editForm.validateFields();
      
      // 构建属性数据 - 支持单选和多选
      const updatedAttributes: ProductAttribute[] = Object.entries(editingAttributes)
        .filter(([_, value]) => value)
        .map(([attrId, value]) => {
          const attr = categoryAttributes.find(a => a.attribute_id === Number(attrId));
          const isMultiSelect = attr?.is_collection || (attr?.max_value_count && attr.max_value_count > 1);
          
          // 处理值
          let valueId: number | string;
          let valueText: string;
          
          if (isMultiSelect && Array.isArray(value)) {
            // 多选：逗号分隔的ID
            valueId = value.join(',');
            // 获取所有选中项的文本
            const texts = value.map(vid => attr?.values?.find(v => v.value_id === vid)?.value).filter(Boolean);
            valueText = texts.join(', ');
          } else if (typeof value === 'number') {
            // 单选
            valueId = value;
            valueText = attr?.values?.find(v => v.value_id === value)?.value || '';
          } else {
            // 文本输入
            valueId = 0;
            valueText = String(value);
          }
          
          return {
            attribute_id: Number(attrId),
            attribute_name: attr?.attribute_name || attr?.name || '',
            attribute_type: attr?.attribute_type || attr?.type || '',
            dictionary_id: attr?.dictionary_id,
            group_name: attr?.group_name,
            is_required: attr?.is_required,
            is_collection: attr?.is_collection,
            max_value_count: attr?.max_value_count,
            value_id: valueId,
            value: valueText,
          };
        });
      
      // 更新本地数据
      const updatedProducts = products.map(p => {
        if (p.id === editingProduct?.id) {
          // 重新计算利润率
          const sourcePrice = p.source_price || 0;
          const newPrice = values.ozon_price;
          const cost = sourcePrice * 13 * 1.2; // 成本核算
          const newProfitRate = ((newPrice - cost) / newPrice) * 100;
          
          return {
            ...p,
            ozon_price: values.ozon_price,
            ozon_stock: values.ozon_stock,
            profit_rate: newProfitRate,
            attributes: updatedAttributes,
          };
        }
        return p;
      });
      
      setProducts(updatedProducts);
      setFilteredProducts(updatedProducts);
      message.success('商品信息已更新');
      setEditVisible(false);

      // 调用API保存到后端
      try {
        // 将attributes数组转换为字典格式 {attribute_id: {...}}
        const attributesDict: Record<string, any> = {};
        updatedAttributes.forEach((attr: any) => {
          attributesDict[attr.attribute_id] = attr;
        });

        // 保存到本地数据库
        await ozonApi.updateDbProduct(editingProduct!.id, {
          price: values.ozon_price,
          stock: values.ozon_stock,
          attributes: attributesDict,
          images: editingImages,
          primary_image: primaryImage,
        });

        // 如果有图片变更，推送到Ozon
        if (editingProduct?.offer_id && (editingImages.length > 0 || primaryImage)) {
          try {
            const allImages = primaryImage ? [primaryImage, ...editingImages.filter((img: string) => img !== primaryImage)] : editingImages;
            await ozonApi.importProductImages({
              offer_id: editingProduct.offer_id,
              images: allImages,
            });
            message.success('已同步到后端数据库并推送到Ozon');
          } catch (ozonError) {
            console.error('Failed to push images to Ozon:', ozonError);
            message.warning('已保存到数据库，但推送到Ozon失败');
          }
        } else {
          message.success('已同步到后端数据库');
        }
      } catch (e: any) {
        console.error('Failed to sync to backend:', e);
        const errorMsg = e?.response?.data?.detail || e?.message || '未知错误';
        message.error(`同步到后端失败: ${errorMsg}`);
      }
    } catch (error: any) {
      console.error('Failed to save:', error);
      const errorMsg = error?.response?.data?.detail || error?.message || '未知错误';
      message.error(`保存失败: ${errorMsg}`);
    } finally {
      setSaving(false);
    }
  };

  const columns: ColumnsType<OzonProduct> = [
    {
      title: '图片',
      dataIndex: 'primary_image',
      key: 'primary_image',
      width: 70,
      render: (img: string) => img ? <img src={img} alt="商品图" style={{ width: 50, height: 50, objectFit: 'cover', borderRadius: 4 }} /> : '-',
    },
    {
      title: 'SKU',
      dataIndex: 'offer_id',
      key: 'offer_id',
      width: 120,
    },
    {
      title: '商品名称',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 200,
    },
    {
      title: 'Ozon售价(₽)',
      dataIndex: 'ozon_price',
      key: 'ozon_price',
      width: 90,
      render: (price: number) => `₽${price?.toFixed(2) || 0}`,
    },
    {
      title: '状态',
      dataIndex: 'platform_status',
      key: 'platform_status',
      width: 60,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
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
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic 
              title="Ozon商品总数" 
              value={products.length} 
              prefix={<ShopOutlined />} 
            />
          </Card>
        </Col>
      </Row>

      <Card 
        title="Ozon商品列表"
        extra={
          <Space>
            <Search
              placeholder="搜索SKU或商品名称"
              onSearch={setSearchText}
              style={{ width: 250 }}
              allowClear
            />
            <Button icon={<SyncOutlined />} onClick={handleSync} loading={syncing}>同步Ozon商品</Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={filteredProducts}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="商品详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={700}
      >
        {selectedProduct && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="SKU" span={2}>
              {selectedProduct.sku}
            </Descriptions.Item>
            <Descriptions.Item label="SPU" span={2}>
              {selectedProduct.spu}
            </Descriptions.Item>
            <Descriptions.Item label="商品名称" span={2}>
              {selectedProduct.title}
            </Descriptions.Item>
            <Descriptions.Item label="采购价">
              ¥{selectedProduct.source_price?.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="供应商">
              {selectedProduct.source_supplier || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="Ozon商品ID">
              {selectedProduct.ozon_product_id}
            </Descriptions.Item>
            <Descriptions.Item label="Ozon售价">
              ₽{selectedProduct.ozon_price?.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="库存">
              {selectedProduct.ozon_stock}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              {getStatusTag(selectedProduct.platform_status)}
            </Descriptions.Item>
            <Descriptions.Item label="利润率">
              {selectedProduct.profit_rate}%
            </Descriptions.Item>
            <Descriptions.Item label="30天销量">
              {selectedProduct.sales_30d}
            </Descriptions.Item>
            <Descriptions.Item label="最后同步" span={2}>
              {selectedProduct.last_synced}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      {/* 编辑弹窗 */}
      <Modal
        title="编辑商品"
        open={editVisible}
        onCancel={() => setEditVisible(false)}
        onOk={handleSaveEdit}
        okButtonProps={{ loading: saving }}
        okText={saving ? '保存中...' : '保存'}
        width={800}
      >
        {editingProduct && (
          <Form form={editForm} layout="vertical">
            <Tabs 
              activeKey={activeTab} 
              onChange={setActiveTab}
              items={[
                { key: "basic", label: "基础信息", children: renderBasicInfoTab() },
                { key: "images", label: "图片", children: renderImagesTab() },
                { key: "attributes", label: "属性", children: renderAttributesTab() },
              ]}
            />
          </Form>
        )}
      </Modal>
    </div>
  );
};

export default OzonProductsPage;
