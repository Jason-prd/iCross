import { useState } from "react";
import { Tabs, Card } from "antd";
import { ShopOutlined, DatabaseOutlined } from "@ant-design/icons";
import Products from "./Products";
import OzonProducts from "./OzonProducts";

const { TabPane } = Tabs;

export default function ProductManagement() {
  const [activeTab, setActiveTab] = useState<string>("library");

  const handleTabChange = (key: string) => {
    setActiveTab(key);
  };

  return (
    <div>
      <Card style={{ height: "calc(100vh - 48px - 48px)" }}>
        <Tabs activeKey={activeTab} onChange={handleTabChange}>
          <TabPane
            tab={
              <span>
                <DatabaseOutlined />
                商品库
              </span>
            }
            key="library"
          >
            <Products />
          </TabPane>
          <TabPane
            tab={
              <span>
                <ShopOutlined />
                Ozon
              </span>
            }
            key="ozon"
          >
            <OzonProducts />
          </TabPane>
          <TabPane
            tab={
              <span>
                <ShopOutlined />
                Amazon
              </span>
            }
            key="amazon"
            disabled
          >
            <div style={{ padding: 40, textAlign: "center", color: "#999" }}>
              Amazon集成开发中
            </div>
          </TabPane>
          <TabPane
            tab={
              <span>
                <ShopOutlined />
                Shopify
              </span>
            }
            key="shopify"
            disabled
          >
            <div style={{ padding: 40, textAlign: "center", color: "#999" }}>
              Shopify集成开发中
            </div>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
}
