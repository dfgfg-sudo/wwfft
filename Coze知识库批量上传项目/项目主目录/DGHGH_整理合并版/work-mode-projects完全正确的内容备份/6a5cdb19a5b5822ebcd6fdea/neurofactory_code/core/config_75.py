UnifiedIntelligentAutomationSuperHub/
├── openapi.yaml                 # 完整合并的 OpenAPI 规范
├── coze-plugin.json             # Coze 插件配置
├── plugin-ide.js                # Coze 插件 IDE 代码
├── README.md                    # 项目说明
├── src/
│   ├── core/                    # 核心引擎
│   │   ├── workflow/            # 工作流引擎
│   │   ├── ai/                  # AI增强引擎
│   │   ├── repair/              # 自愈引擎
│   │   └── plugin/              # 插件引擎
│   ├── api/                     # API 路由与控制器
│   ├── plugins/                 # 插件管理
│   ├── services/                # 业务服务
│   │   ├── emergency/           # 紧急处理服务
│   │   ├── heritage/            # 文化遗产服务
│   │   └── training/            # 模型训练服务
│   └── utils/                   # 工具函数
├── docker/
│   └── Dockerfile               # 容器部署文件
├── tests/                       # 单元测试与集成测试
├── config/
│   ├── nginx.conf               # Nginx配置
│   └── grafana/                 # Grafana配置
├── deploy.sh                    # 一键部署脚本
├── test.sh                      # 自动化测试脚本
└── docs/
    ├── architecture.md          # 详细架构设计
    └── api-reference.md         # API 详细参考