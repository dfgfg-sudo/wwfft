"""
flowchart LR
    subgraph 一环[第一环：情报]
        A1[YouTube Topic Insights]
        A2[神策数据<br>360°用户画像]
        A3[GPTube<br>情绪分析]
    end

    subgraph 二环[第二环：生产]
        B1[爱奇艺纳逗Pro<br>编剧/分镜/视效]
        B2[万兴ReelClaw<br>全链路创作]
        B3[Zopia<br>AI视频导演]
    end

    subgraph 三环[第三环：品控]
        C1[Higgsfield<br>相似性检测]
        C2[Vidupe<br>内容级查重]
        C3[AI深度剪辑<br>数字水印]
    end

    subgraph 四环[第四环：合规]
        D1[阿里云AI护栏<br>内容安全审核]
        D2[天融信多模态<br>防伪溯源]
        D3[内容标注要求<br>AI内容标注]
    end

    subgraph 五环[第五环：变现]
        E1[平台分成/商单]
        E2[平台激励计划]
        E3[垂直领域<br>短剧/代言人]
        E4[规模化自动化<br>智能体矩阵]
    end

    一环 --> 二环 --> 三环 --> 四环 --> 五环
"""
