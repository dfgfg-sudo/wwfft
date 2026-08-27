{
  "workflow": {
    "name": "AI短视频自动生成",
    "nodes": [
      {
        "id": "start",
        "type": "start",
        "position": {"x": 100, "y": 100},
        "data": {
          "parameters": {
            "zhuti": "智能语音中控屏"
          }
        }
      },
      {
        "id": "llm_prompt",
        "type": "llm",
        "position": {"x": 300, "y": 100},
        "data": {
          "model": "豆包·1.8",
          "parameters": {
            "input": "{{start.zhuti}}",
            "system_prompt": "你是一位经验丰富且极具创意的商品宣传图生图提示词及视频提示词生成专家...",
            "temperature": 0.7,
            "max_tokens": 2048,
            "seed": 42
          }
        }
      },
      {
        "id": "image_gen",
        "type": "image_generation",
        "position": {"x": 500, "y": 50},
        "data": {
          "model": "豆包·4.5",
          "parameters": {
            "prompt": "{{llm_prompt.tupian}}",
            "seed": 42,
            "width": 1024,
            "height": 1024
          }
        }
      },
      {
        "id": "video_gen",
        "type": "video_generation",
        "position": {"x": 500, "y": 200},
        "data": {
          "model": "doubao-seedance.dit",
          "parameters": {
            "prompt": "{{llm_prompt.shipin}}",
            "seed": 42,
            "duration": 10,
            "ratio": "16:9",
            "resolution": "1080p"
          }
        }
      },
      {
        "id": "audio_gen",
        "type": "audio_generation",
        "position": {"x": 500, "y": 350},
        "data": {
          "model": "豆包·4.5",
          "parameters": {
            "keyword": "科技感 轻快",
            "seed": 42
          }
        }
      },
      {
        "id": "compose",
        "type": "video_composition",
        "position": {"x": 750, "y": 200},
        "data": {
          "parameters": {
            "video": "{{video_gen.video_msg}}",
            "audio": "{{audio_gen.message}}",
            "is_audio_message": true
          }
        }
      },
      {
        "id": "end",
        "type": "end",
        "position": {"x": 950, "y": 200},
        "data": {
          "parameters": {
            "output": "{{compose.sitmessage}}"
          }
        }
      }
    ],
    "edges": [
      {"id": "e1", "source": "start", "target": "llm_prompt"},
      {"id": "e2", "source": "llm_prompt", "target": "image_gen", "sourceHandle": "tupian"},
      {"id": "e3", "source": "llm_prompt", "target": "video_gen", "sourceHandle": "shipin"},
      {"id": "e4", "source": "llm_prompt", "target": "audio_gen", "sourceHandle": "keyword"},
      {"id": "e5", "source": "image_gen", "target": "compose", "sourceHandle": "msg"},
      {"id": "e6", "source": "video_gen", "target": "compose", "sourceHandle": "video_msg"},
      {"id": "e7", "source": "audio_gen", "target": "compose", "sourceHandle": "message"},
      {"id": "e8", "source": "compose", "target": "end"}
    ]
  }
}