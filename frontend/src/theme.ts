import { ThemeConfig } from "antd";

export const theme: ThemeConfig = {
  token: {
    // 字体大小调整
    fontSize: 12,
    fontSizeSM: 11,
    fontSizeLG: 13,
    fontSizeXL: 14,

    // 行高调整
    lineHeight: 1.4,
    lineHeightSM: 1.3,
    lineHeightLG: 1.5,

    // 间距调整
    padding: 8,
    paddingXS: 4,
    paddingSM: 6,
    paddingLG: 12,
    paddingXL: 16,

    margin: 8,
    marginXS: 4,
    marginSM: 6,
    marginLG: 12,
    marginXL: 16,

    // 组件尺寸
    controlHeight: 28,
    controlHeightSM: 24,
    controlHeightLG: 32,

    // 边框圆角
    borderRadius: 4,
    borderRadiusSM: 3,
    borderRadiusLG: 6,

    // 颜色微调
    colorPrimary: "#1890ff",
    colorSuccess: "#52c41a",
    colorWarning: "#faad14",
    colorError: "#ff4d4f",
    colorInfo: "#1890ff",
    colorTextBase: "#262626",
    colorBgContainer: "#ffffff",
    colorBgLayout: "#f5f5f5",

    // 组件内边距
    paddingContentHorizontal: 12,
    paddingContentVertical: 8,
  },
  components: {
    // Button 组件调整
    Button: {
      paddingInline: 12,
      paddingBlock: 4,
      controlHeight: 28,
    },
    // Table 组件调整
    Table: {
      fontSize: 12,
      padding: 8,
      paddingXS: 4,
      paddingSM: 6,
      paddingLG: 12,
      cellPaddingBlock: 6,
      cellPaddingInline: 8,
    },
    // Card 组件调整
    Card: {
      padding: 12,
      paddingLG: 16,
    },
    // Form 组件调整
    Form: {
      labelFontSize: 12,
      labelHeight: 28,
      itemMarginBottom: 16,
    },
    // Input 组件调整
    Input: {
      controlHeight: 28,
      controlHeightSM: 24,
      controlHeightLG: 32,
      paddingInline: 8,
      paddingBlock: 4,
    },
    // Select 组件调整
    Select: {
      controlHeight: 28,
      controlHeightSM: 24,
      controlHeightLG: 32,
    },
    // Modal 组件调整
    Modal: {
      padding: 16,
      paddingMD: 20,
      paddingLG: 24,
    },
    // Tabs 组件调整
    Tabs: {
      horizontalItemPadding: "8px 12px",
      horizontalItemGutter: 8,
    },
  },
};
