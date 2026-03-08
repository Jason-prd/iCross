// -*- coding: utf-8 -*-
/**
 * API服务
 * 封装所有后端API调用
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 获取token的函数
const getAuthToken = () => {
  try {
    const authData = localStorage.getItem('icross-auth');
    if (authData) {
      const parsed = JSON.parse(authData);
      return parsed?.state?.token || parsed?.token;
    }
  } catch (e) {
    // ignore
  }
  return null;
};

// 通用请求方法
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options?.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `API Error: ${response.statusText}`);
  }
  
  const data = await response.json();
  
  // 如果返回的是数组，直接包装成 { data, meta }
  // 如果返回的是对象，直接返回
  if (Array.isArray(data)) {
    return { data, meta: { total: data.length } } as T;
  }
  
  return data as T;
}

// ==================== Dashboard API ====================

export interface DashboardStats {
  selection_total: number;
  selection_selected: number;
  selection_pending: number;
  selection_listed: number;
  order_total: number;
  order_pending: number;
  order_processing: number;
  order_completed: number;
  order_total_amount: number;
  dropship_total: number;
  dropship_pending: number;
  dropship_shipped: number;
  dropship_total_profit: number;
  product_total: number;
  product_low_stock: number;
  product_avg_profit_rate: number;
}

export const dashboardApi = {
  getStats: () => request<DashboardStats>('/dashboard/stats'),
  getLowStock: (limit = 10) => request<any>(`/dashboard/low-stock?limit=${limit}`),
  getRecentOrders: (limit = 5) => request<any>(`/dashboard/recent-orders?limit=${limit}`),
};

// ==================== Selection API ====================

export interface SelectionProduct {
  id: string;
  master_sku: string;
  title: string;
  selection_status: string;
  listing_status: string;
  source_url?: string;
  source_price?: number;
  source_supplier?: string;
  category?: string;
  created_at: string;
}

export interface SelectionStats {
  total: number;
  selected: number;
  pending: number;
  listed: number;
}

export const selectionApi = {
  list: (params?: { selection_status?: string; listing_status?: string; search?: string; page?: number; limit?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/selection?${query}`);
  },
  getStats: () => request<SelectionStats>('/selection/stats'),
  getById: (id: string) => request<SelectionProduct>(`/selection/${id}`),
  listProduct: (id: string) => request<any>(`/selection/${id}/list`, { method: 'POST' }),
};

// ==================== Dropship API ====================

export interface DropshipOrder {
  id: string;
  platform_order_id: string;
  sku: string;
  quantity: number;
  sale_price: number;
  purchase_cost: number;
  shipping_cost: number;
  total_cost: number;
  profit: number;
  profit_rate: number;
  status: string;
  supplier_order_id?: string;
  tracking_number?: string;
  shipping_carrier?: string;
  order_placed_at?: string;
  supplier_order_at?: string;
  shipped_at?: string;
  delivered_at?: string;
  created_at: string;
}

export interface DropshipStats {
  total: number;
  pending: number;
  processing: number;
  shipped: number;
  delivered: number;
  total_profit: number;
}

export const dropshipApi = {
  list: (params?: { status?: string; search?: string; page?: number; limit?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/dropship?${query}`);
  },
  getStats: () => request<DropshipStats>('/dropship/stats'),
  getById: (id: string) => request<DropshipOrder>(`/dropship/${id}`),
  create: (data: { platform_order_id: string; sku: string; quantity: number; sale_price: number }) =>
    request<any>('/dropship/create', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  process: (id: string) =>
    request<any>(`/dropship/${id}/process`, { method: 'POST' }),
  ship: (id: string, data: { tracking_number: string; carrier: string }) =>
    request<any>(`/dropship/${id}/ship`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ==================== Ozon Products API ====================

export interface OzonProduct {
  id: string;
  sku: string;
  spu: string;
  title: string;
  ozon_price: number;
  ozon_stock: number;
  ozon_product_id: string;
  platform_status: string;
  listing_status: string;
  profit_rate: number;
  sales_30d: number;
  last_synced: string;
}

export const ozonProductApi = {
  list: (params?: { search?: string; page?: number; limit?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/products?${query}`);
  },
  getById: (id: string) => request<OzonProduct>(`/ozon/products/${id}`),
  sync: () => request<any>('/ozon/sync/products', { method: 'POST' }),
};

// ==================== Orders API ====================

export interface Order {
  id: string;
  order_number: string;
  platform_order_id: string;
  customer_name: string;
  total_amount: number;
  status: string;
  fulfillment_status: string;
  payment_status: string;
  created_at: string;
}

export const orderApi = {
  list: (params?: { status?: string; search?: string; page?: number; limit?: number; payment_status?: string; fulfillment_status?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/orders?${query}`);
  },
  getAll: (params?: { status?: string; search?: string; page?: number; limit?: number; payment_status?: string; fulfillment_status?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/orders?${query}`);
  },
  getById: (id: string) => request<any>(`/orders/${id}`),
  getOne: (id: string) => request<any>(`/orders/${id}`),
  sync: () => request<any>('/ozon/sync/orders', { method: 'POST' }),
  updateStatus: (id: string, status: string) => request<any>(`/orders/${id}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  }),
};

// Legacy alias
export const ordersApi = orderApi;

// ==================== Customers API ====================

export const customersApi = {
  list: () => request<any>('/customers'),
  getAll: () => request<any>('/customers'),
  getById: (id: string) => request<any>(`/customers/${id}`),
  getOne: (id: string) => request<any>(`/customers/${id}`),
  getCommunications: (id: string) => request<any>(`/customers/${id}/communications`),
  addCommunication: (id: string, data: any) => request<any>(`/customers/${id}/communications`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

// ==================== Shops API ====================

export const shopsApi = {
  list: () => request<any>('/shops'),
  getAll: (params?: { platform?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/shops?${query}`);
  },
  getById: (id: string) => request<any>(`/shops/${id}`),
  sync: () => request<any>('/shops/sync', { method: 'POST' }),
  create: (data: any) => request<any>('/shops', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id: string, data: any) => request<any>(`/shops/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id: string) => request<any>(`/shops/${id}`, { method: 'DELETE' }),
};

// ==================== Products API ====================

export const productsApi = {
  list: (params?: { search?: string; page?: number; limit?: number; status?: string; q?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/products?${query}`);
  },
  getAll: (params?: { search?: string; page?: number; limit?: number; status?: string; q?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/products?${query}`);
  },
  getById: (id: string) => request<any>(`/products/${id}`),
  sync: () => request<any>('/products/sync', { method: 'POST' }),
  create: (data: any) => request<any>('/products', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id: string, data: any) => request<any>(`/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id: string) => request<any>(`/products/${id}`, { method: 'DELETE' }),
};

// ==================== Inventory API ====================

// Helper to filter undefined values
const filterParams = (params?: Record<string, any>): Record<string, any> => {
  if (!params) return {};
  const filtered: Record<string, any> = {};
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      filtered[key] = value;
    }
  });
  return filtered;
};

export const inventoryApi = {
  list: (params?: { low_stock?: boolean; page?: number; limit?: number }) => {
    const filtered = filterParams(params);
    const query = new URLSearchParams(filtered).toString();
    return request<any>(`/inventory?${query}`);
  },
  getAll: (params?: { low_stock?: boolean; page?: number; limit?: number }) => {
    const filtered = filterParams(params);
    const query = new URLSearchParams(filtered).toString();
    return request<any>(`/inventory?${query}`);
  },
  getById: (id: string) => request<any>(`/inventory/${id}`),
  update: (id: string, data: any) => request<any>(`/inventory/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  adjust: (id: string, data: any) => request<any>(`/inventory/${id}/adjust`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  createWarehouse: (data: any) => request<any>('/inventory/warehouses', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  getWarehouses: () => request<any>('/inventory/warehouses'),
};

// ==================== Ozon API ====================

export const ozonApi = {
  listProducts: (params?: { search?: string; page?: number; limit?: number }) => {
    const filtered = filterParams(params);
    const query = new URLSearchParams(filtered).toString();
    return request<any>(`/ozon/db/products?${query}`);
  },
  syncProducts: () => request<any>('/ozon/sync/products', { method: 'POST' }),
  syncOrders: (shopId?: string, daysBack?: number) => {
    const params = new URLSearchParams();
    if (shopId) params.append('shop_id', shopId);
    if (daysBack) params.append('days_back', String(daysBack));
    const query = params.toString();
    return request<any>(`/ozon/sync/orders${query ? '?' + query : ''}`, { method: 'POST' });
  },
  getConfig: () => request<any>('/ozon/config'),
  updateConfig: (data: any) => request<any>('/ozon/config', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  syncCategoryTree: () => request<any>('/ozon/sync/category-tree', { method: 'POST' }),
  syncCategoryAttributes: (params: { description_category_id: number; type_id: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/category-attributes/all?${query}`, { method: 'POST' });
  },
  getDbProducts: (params?: { page?: number; limit?: number; q?: string; visibility?: string; sku?: string; offer_id?: string; category_id?: number; status_filter?: string; shop_id?: string }) => {
    const filtered = filterParams(params);
    const query = new URLSearchParams(filtered).toString();
    return request<any>(`/ozon/db/products?${query}`);
  },
  getStats: () => request<any>('/ozon/stats'),
  getCategories: () => request<any>('/ozon/categories'),
  getAllCategoryTree: () => request<any>('/ozon/category-tree/nested'),
  getCategoryAttributes: (params: { description_category_id: number; type_id: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/category-attributes/all?${query}`);
  },
  getAttributeValues: (params: { description_category_id: number; type_id: number; attribute_id: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/category-attribute/values?${query}`);
  },
  getAttributeValuesRemote: (params: { description_category_id: number; type_id: number; attribute_id: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/category-attribute/values/remote?${query}`);
  },
  // 新的描述性分类API
  getDescriptionCategoryTree: (language: string = "ZH_HANS") => {
    return request<any>('/ozon/description-category/tree', {
      method: 'POST',
      body: JSON.stringify({ language }),
    });
  },
  getDescriptionCategoryAttribute: (params: { description_category_id: number; type_id: number; language?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/description-category/attribute?${query}`, { method: 'POST' });
  },
  getDescriptionCategoryAttributeValues: (params: { description_category_id: number; type_id: number; attribute_id: number; language?: string; limit?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/description-category/attribute/values?${query}`, { method: 'POST' });
  },
  searchDescriptionCategoryAttributeValues: (params: { description_category_id: number; type_id: number; attribute_id: number; value: string; limit?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(`/ozon/description-category/attribute/values/search?${query}`, { method: 'POST' });
  },
  updateDbProduct: (id: string, data: any) => request<any>(`/ozon/db/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  pushProduct: (id: string) => request<any>(`/ozon/products/${id}/push`, { method: 'POST' }),
  archiveProduct: (id: string) => request<any>(`/ozon/products/${id}/archive`, { method: 'POST' }),
  unarchiveProduct: (id: string) => request<any>(`/ozon/products/${id}/unarchive`, { method: 'POST' }),
  getDeliveryMethods: (shopId?: string) => {
    const url = shopId ? `/ozon/delivery-methods?shop_id=${shopId}` : '/ozon/delivery-methods';
    return request<any>(url);
  },
  updateProductPrices: (data: any) => request<any>('/ozon/products/prices/batch', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  updateProductStocks: (data: any) => request<any>('/ozon/products/stocks/batch', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  // 新增：获取商品价格列表
  getProductPrices: (params?: { shop_id?: string; product_ids?: string }) => {
    const filtered = filterParams(params);
    const query = new URLSearchParams(filtered).toString();
    return request<any>(`/ozon/products/prices?${query}`);
  },
  // 新增：获取商品库存列表
  getProductStocks: (params?: { shop_id?: string; product_ids?: string }) => {
    const filtered = filterParams(params);
    const query = new URLSearchParams(filtered).toString();
    return request<any>(`/ozon/products/stocks?${query}`);
  },
  // 新增：测试Ozon连接
  testConnection: () => request<any>('/ozon/test-connection'),
  // 新增：获取卖家信息
  getSellerInfo: () => request<any>('/ozon/seller-info'),
  // 新增：获取Ozon仓库列表
  getOzonWarehouses: () => request<any>('/ozon/warehouses'),
  // 新增：导入商品图片到Ozon
  importProductImages: (data: { offer_id: string; images: string[] }) => request<any>('/ozon/products/images', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  // 新增：获取FBO订单详情
  getFboOrderDetail: (postingNumber: string, shopId?: string) => {
    const params = new URLSearchParams();
    if (shopId) params.append('shop_id', shopId);
    const query = params.toString();
    return request<any>(`/ozon/orders/fbo/${postingNumber}${query ? '?' + query : ''}`);
  },
  // 新增：获取FBS订单详情
  getFbsOrderDetail: (postingNumber: string, shopId?: string) => {
    const params = new URLSearchParams();
    if (shopId) params.append('shop_id', shopId);
    const query = params.toString();
    return request<any>(`/ozon/orders/fbs/${postingNumber}${query ? '?' + query : ''}`);
  },
  // 新增：获取待发货订单
  getUnfulfilledPostings: (shopId?: string) => {
    const params = new URLSearchParams();
    if (shopId) params.append('shop_id', shopId);
    const query = params.toString();
    return request<any>(`/ozon/orders/unfulfilled${query ? '?' + query : ''}`);
  },
};

// ==================== Auth API ====================

export const authApi = {
  login: (username: string, password: string) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    return request<any>('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });
  },
  logout: () => request<any>('/auth/logout', { method: 'POST' }),
  me: () => request<any>('/auth/me'),
};
