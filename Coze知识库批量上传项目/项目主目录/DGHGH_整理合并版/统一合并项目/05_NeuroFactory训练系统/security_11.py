"""
flowchart TD
    subgraph A[第一层：数据与选题]
        A1[开始节点<br>用户输入主题/实时热点获取]
    end

    subgraph B[第二层：内容生成]
        B1[大模型节点<br>写图片提示词]
        B2[大模型节点<br>写视频提示词]
        B3[大模型节点<br>写配音脚本]
    end

    subgraph C[第三层：素材生产]
        C1[图像生成节点<br>生成画面素材]
        C2[视频生成节点<br>生成视频片段]
        C3[音频生成节点<br>生成配音/BGM]
    end

    subgraph D[第四层：审核与合规]
        D1[内容安全检测<br>违禁词/敏感信息过滤]
        D2[AI标识标注<br>合规发布]
    end

    subgraph E[第五层：剪辑合成]
        E1[视频合成节点<br>画面+配音+BGM]
        E2[字幕生成节点<br>自动字幕]
    end

    subgraph F[第六层：发布与变现]
        F1[多平台分发]
        F2[接单平台交付]
        F3[收益分析反馈]
    end

    A --> B --> C --> D --> E --> F
    F -.->|数据反馈优化| A
"""
