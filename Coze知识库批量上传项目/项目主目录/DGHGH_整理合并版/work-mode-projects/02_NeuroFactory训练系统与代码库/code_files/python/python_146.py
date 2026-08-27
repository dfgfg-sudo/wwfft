# 示例插件模板
from coze_plugins.plugin_generator import PluginGenerator

generator = PluginGenerator()
plugin = generator.generate({
    "name": "我的插件",
    "description": "这是一个示例插件",
    "functions": ["data_processing", "model_training"]
})