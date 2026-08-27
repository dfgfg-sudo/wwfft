const JSZip = require('jszip');
const JsonParser = require('./json-parser');
const YamlParser = require('./yaml-parser');

class ZipParser {
  constructor() {
    this.jsonParser = new JsonParser();
    this.yamlParser = new YamlParser();
  }
  
  async parse(zipContent) {
    const zip = new JSZip();
    
    try {
      // 加载ZIP文件
      const zipData = await zip.loadAsync(zipContent);
      
      // 查找配置文件
      const configFiles = [];
      
      zipData.forEach((relativePath, file) => {
        if (!file.dir) {
          const fileName = relativePath.split('/').pop();
          if (fileName.match(/^(workflow|config)\.(json|yaml|yml)$/i)) {
            configFiles.push({
              path: relativePath,
              name: fileName,
              file: file
            });
          }
        }
      });
      
      if (configFiles.length === 0) {
        throw new Error('ZIP文件中未找到配置文件');
      }
      
      // 使用第一个配置文件
      const mainConfig = configFiles[0];
      const content = await mainConfig.file.async('text');
      
      // 根据扩展名选择解析器
      const ext = mainConfig.name.split('.').pop().toLowerCase();
      
      if (ext === 'json') {
        return this.jsonParser.parse(content);
      } else {
        return this.yamlParser.parse(content);
      }
      
    } catch (error) {
      throw new Error(`解析ZIP文件失败: ${error.message}`);
    }
  }
}

module.exports = ZipParser;