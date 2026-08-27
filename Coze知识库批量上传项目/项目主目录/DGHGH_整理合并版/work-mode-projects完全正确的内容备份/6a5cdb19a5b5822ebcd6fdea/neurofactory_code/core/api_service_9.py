flowchart TD
    subgraph 资源库基础操作层
        A1[创建工作流/智能体]
        A2[更新/版本控制]
        A3[删除/归档清理]
        A4[查看引用关系]
    end

    subgraph 多范围资源管理层
        B1[个人空间资源]
        B2[团队空间协作]
        B3[项目空间隔离]
        B4[跨空间引用]
    end

    subgraph 多服务连接层
        C1[插件宇宙-136+插件]
        C2[自定义API连接器]
        C3[数据库集成]
    end

    subgraph 多端点处理层
        D1[链接读取插件<br/>网页/PDF/图片]
        D2[HTTP请求节点<br/>RESTful]
        D3[Webhook实时触发]
        D4[定时任务批量处理]
    end

    subgraph AI编程增强层
        E1[代码节点<br/>Python/JS]
        E2[大模型节点<br/>AI推理]
        E3[变量聚合<br/>智能合并]
    end

    subgraph 自动化运维层
        F1[自动整理脚本]
        F2[监控告警]
        F3[灰度发布]
        F4[错误处理与重试]
    end

    资源库基础操作层 --> 多范围资源管理层
    多范围资源管理层 --> 多服务连接层
    多服务连接层 --> 多端点处理层
    多端点处理层 --> AI编程增强层
    AI编程增强层 --> 自动化运维层