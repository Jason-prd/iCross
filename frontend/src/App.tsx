import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ConfigProvider, Layout } from "antd";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import DashboardNew from "./pages/DashboardNew";
import Shops from "./pages/Shops";
import Products from "./pages/Products";
import OzonProducts from "./pages/OzonProducts";
import OzonProductsNew from "./pages/OzonProductsNew";
import OzonConfig from "./pages/OzonConfig";
import Orders from "./pages/Orders";
import OrdersNew from "./pages/OrdersNew";
import Inventory from "./pages/Inventory";
import Customers from "./pages/Customers";
import SelectionProducts from "./pages/SelectionProducts";
import DropshipOrders from "./pages/DropshipOrders";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import { useAuthStore } from "./stores/auth";
import { theme } from "./theme";

const { Content } = Layout;

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <ConfigProvider theme={theme}>
                <Layout style={{ minHeight: "100vh" }}>
                  <Sidebar />
                  <Layout>
                    <Header />
                    <Content
                      style={{
                        margin: "16px",
                        padding: "16px",
                        background: "#fff",
                        borderRadius: "4px",
                      }}
                    >
                      <Routes>
                        <Route
                          path="/"
                          element={<Navigate to="/dashboard" replace />}
                        />
                        {/* 运营仪表盘 */}
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/dashboard/new" element={<DashboardNew />} />
                        
                        {/* 店铺管理 */}
                        <Route path="/shops" element={<Shops />} />
                        
                        {/* 商品管理 */}
                        <Route
                          path="/products"
                          element={<Navigate to="/products/library" replace />}
                        />
                        <Route
                          path="/products/library"
                          element={<Products />}
                        />
                        {/* 选品管理 - 新增 */}
                        <Route
                          path="/products/selection"
                          element={<SelectionProducts />}
                        />
                        {/* Ozon商品 */}
                        <Route
                          path="/products/ozon"
                          element={<OzonProducts />}
                        />
                        <Route
                          path="/products/amazon"
                          element={
                            <div style={{ padding: 40, textAlign: "center", color: "#999" }}>
                              Amazon集成开发中
                            </div>
                          }
                        />
                        <Route
                          path="/products/shopify"
                          element={
                            <div style={{ padding: 40, textAlign: "center", color: "#999" }}>
                              Shopify集成开发中
                            </div>
                          }
                        />
                        
                        {/* 订单管理 */}
                        <Route path="/orders" element={<Orders />} />
                        <Route path="/orders/new" element={<OrdersNew />} />
                        
                        {/* 代发订单 - 新增 */}
                        <Route path="/orders/dropship" element={<DropshipOrders />} />
                        
                        {/* 库存 */}
                        <Route path="/inventory" element={<Inventory />} />
                        
                        {/* 客户 */}
                        <Route path="/customers" element={<Customers />} />
                        
                        {/* 设置 */}
                        <Route
                          path="/settings/ozon"
                          element={<OzonConfig />}
                        />
                      </Routes>
                    </Content>
                  </Layout>
                </Layout>
              </ConfigProvider>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
