import { useState, useEffect } from "react";
import {
  Card,
  Button,
  Table,
  Space,
  Tag,
  message,
  Row,
  Col,
  Statistic,
  Alert,
  Select,
} from "antd";
import {
  SyncOutlined,
  SettingOutlined,
  DatabaseOutlined,
} from "@ant-design/icons";
import { ozonApi } from "../services/api";

interface SyncLog {
  id: string;
  type: string;
  status: string;
  message: string;
  languages?: string[];
  created_at: string;
}

interface CategoryStats {
  total_categories: number;
  total_attributes: number;
  total_values: number;
}

export default function OzonConfig() {
  const [syncingCategoryTree, setSyncingCategoryTree] = useState(false);
  const [syncingAttributes, setSyncingAttributes] = useState(false);
  const [language, setLanguage] = useState("ZH_HANS");
  const [stats, setStats] = useState<CategoryStats | null>(null);
  const [logs, setLogs] = useState<SyncLog[]>([]);

  const LANGUAGE_OPTIONS = [
    { value: "ZH_HANS", label: "中文" },
    { value: "EN", label: "English" },
    { value: "RU", label: "Русский" },
  ];

  const fetchStats = async () => {
    try {
      // For now, we'll just show a placeholder
      setStats({
        total_categories: 0,
        total_attributes: 0,
        total_values: 0,
      });
    } catch (error: any) {
      console.error("Failed to fetch stats:", error);
    }
  };

  const handleSyncCategoryTree = async (syncAll: boolean = false) => {
    setSyncingCategoryTree(true);
    try {
      const res = await ozonApi.syncCategoryTree({
        language: syncAll ? "ZH_HANS" : language,
        sync_all: syncAll,
      });
      message.success(res.data.message || "分类树同步成功");
      setLogs((prev) => [
        {
          id: Date.now().toString(),
          type: "category_tree",
          status: "success",
          message: res.data.message,
          languages: res.data.languages,
          created_at: new Date().toISOString(),
        },
        ...prev,
      ]);
      fetchStats();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "分类树同步失败");
      setLogs((prev) => [
        {
          id: Date.now().toString(),
          type: "category_tree",
          status: "error",
          message: error.response?.data?.detail || "分类树同步失败",
          created_at: new Date().toISOString(),
        },
        ...prev,
      ]);
    } finally {
      setSyncingCategoryTree(false);
    }
  };

  const handleSyncAttributes = async (syncAll: boolean = false) => {
    setSyncingAttributes(true);
    try {
      // First get a product to get the category_id and type_id
      const productsRes = await ozonApi.getDbProducts({ limit: 1 });
      if (productsRes.data.data.length === 0) {
        message.warning("请先同步商品数据");
        setSyncingAttributes(false);
        return;
      }

      const product = productsRes.data.data[0];
      const categoryId = product.category_id;
      const typeId = product.type_id;

      if (!categoryId || !typeId) {
        message.warning("商品缺少category_id或type_id，请先同步商品");
        setSyncingAttributes(false);
        return;
      }

      const res = await ozonApi.syncCategoryAttributes({
        description_category_id: categoryId,
        type_id: typeId,
        language: syncAll ? "ZH_HANS" : language,
        sync_all: syncAll,
      });
      message.success(res.data.message || "属性同步成功");
      setLogs((prev) => [
        {
          id: Date.now().toString(),
          type: "attributes",
          status: "success",
          message: res.data.message,
          languages: res.data.languages,
          created_at: new Date().toISOString(),
        },
        ...prev,
      ]);
      fetchStats();
    } catch (error: any) {
      message.error(error.response?.data?.detail || "属性同步失败");
      setLogs((prev) => [
        {
          id: Date.now().toString(),
          type: "attributes",
          status: "error",
          message: error.response?.data?.detail || "属性同步失败",
          created_at: new Date().toISOString(),
        },
        ...prev,
      ]);
    } finally {
      setSyncingAttributes(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const logColumns = [
    {
      title: "类型",
      dataIndex: "type",
      key: "type",
      render: (type: string) => (
        <Tag color={type === "category_tree" ? "blue" : "green"}>
          {type === "category_tree" ? "分类树" : "属性"}
        </Tag>
      ),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag color={status === "success" ? "success" : "error"}>
          {status === "success" ? "成功" : "失败"}
        </Tag>
      ),
    },
    {
      title: "消息",
      dataIndex: "message",
      key: "message",
    },
    {
      title: "语言",
      dataIndex: "languages",
      key: "languages",
      render: (languages?: string[]) =>
        languages?.map((lang) => (
          <Tag key={lang} color="purple">
            {lang}
          </Tag>
        )),
    },
    {
      title: "时间",
      dataIndex: "created_at",
      key: "created_at",
      render: (time: string) => new Date(time).toLocaleString(),
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="分类数量"
              value={stats?.total_categories || 0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="属性数量"
              value={stats?.total_attributes || 0}
              prefix={<SettingOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="属性值数量"
              value={stats?.total_values || 0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="同步日志"
              value={logs.length}
              prefix={<SyncOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="分类树同步"
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Select
              value={language}
              onChange={setLanguage}
              style={{ width: 120 }}
              options={LANGUAGE_OPTIONS}
              disabled={syncingCategoryTree}
            />
            <Button
              type="primary"
              icon={<SyncOutlined spin={syncingCategoryTree} />}
              onClick={() => handleSyncCategoryTree(false)}
              loading={syncingCategoryTree}
            >
              同步 {LANGUAGE_OPTIONS.find((l) => l.value === language)?.label}
            </Button>
            <Button
              icon={<SyncOutlined />}
              onClick={() => handleSyncCategoryTree(true)}
              loading={syncingCategoryTree}
            >
              同步全部语言
            </Button>
          </Space>
        }
      >
        <Alert
          message="分类树同步说明"
          description="同步Ozon平台的商品分类树到本地数据库。支持三种语言：中文、英文、俄语。同步全部语言会依次同步三种语言。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      </Card>

      <Card
        title="属性同步"
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Select
              value={language}
              onChange={setLanguage}
              style={{ width: 120 }}
              options={LANGUAGE_OPTIONS}
              disabled={syncingAttributes}
            />
            <Button
              type="primary"
              icon={<SyncOutlined spin={syncingAttributes} />}
              onClick={() => handleSyncAttributes(false)}
              loading={syncingAttributes}
            >
              同步 {LANGUAGE_OPTIONS.find((l) => l.value === language)?.label}
            </Button>
            <Button
              icon={<SyncOutlined />}
              onClick={() => handleSyncAttributes(true)}
              loading={syncingAttributes}
            >
              同步全部语言
            </Button>
          </Space>
        }
      >
        <Alert
          message="属性同步说明"
          description="同步Ozon指定分类的属性到本地数据库。根据当前商品的category_id和type_id进行同步。需要先同步商品数据。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        <div>
          <p>
            <strong>注意：</strong>属性同步需要指定分类ID和类型ID，系统会自动从已同步的商品中获取。
          </p>
        </div>
      </Card>

      <Card title="同步日志">
        <Table
          columns={logColumns}
          dataSource={logs}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: "暂无同步记录" }}
        />
      </Card>
    </div>
  );
}
