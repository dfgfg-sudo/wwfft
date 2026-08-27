/**
 * 输出处理器
 * 将result按照指定format格式化输出，支持多种输出格式
 */

class OutputHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[output] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[output] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['result'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
  }

  async process() {
    const result = this.inputs.result;
    const format = this.inputs.format || 'json';
    const template = this.inputs.template;
    const pretty = this.inputs.pretty !== false;
    const encoding = this.inputs.encoding || 'utf-8';
    const compress = this.inputs.compress || false;

    let formattedOutput;

    switch (format.toLowerCase()) {
      case 'json':
        formattedOutput = this.formatJSON(result, pretty);
        break;
      case 'xml':
        formattedOutput = this.formatXML(result);
        break;
      case 'yaml':
      case 'yml':
        formattedOutput = this.formatYAML(result);
        break;
      case 'csv':
        formattedOutput = this.formatCSV(result);
        break;
      case 'text':
      case 'plain':
        formattedOutput = this.formatText(result);
        break;
      case 'html':
        formattedOutput = this.formatHTML(result);
        break;
      case 'markdown':
      case 'md':
        formattedOutput = this.formatMarkdown(result);
        break;
      case 'template':
        if (!template) throw new Error('template格式需要template参数');
        formattedOutput = this.formatTemplate(result, template);
        break;
      case 'base64':
        formattedOutput = this.formatBase64(result);
        break;
      default:
        formattedOutput = this.formatJSON(result, pretty);
    }

    // 压缩处理
    if (compress && typeof formattedOutput === 'string') {
      formattedOutput = formattedOutput.replace(/\s+/g, ' ').trim();
    }

    return {
      format: format,
      output: formattedOutput,
      encoding: encoding,
      compressed: compress,
      byte_length: typeof formattedOutput === 'string' ? Buffer.byteLength(formattedOutput, encoding) : 0,
      char_length: typeof formattedOutput === 'string' ? formattedOutput.length : 0,
      executed: true
    };
  }

  formatJSON(data, pretty) {
    try {
      return pretty ? JSON.stringify(data, null, 2) : JSON.stringify(data);
    } catch (e) {
      return JSON.stringify({ error: '无法序列化为JSON', data: String(data) });
    }
  }

  formatXML(data, rootName) {
    rootName = rootName || 'root';
    const buildXML = (obj, name) => {
      name = name || rootName;
      if (obj === null || obj === undefined) return `<${name}></${name}>`;
      if (typeof obj !== 'object') return `<${name}>${obj}</${name}>`;
      if (Array.isArray(obj)) {
        return obj.map(item => buildXML(item, name)).join('');
      }
      let xml = `<${name}>`;
      for (const [key, value] of Object.entries(obj)) {
        xml += buildXML(value, key);
      }
      xml += `</${name}>`;
      return xml;
    };
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + buildXML(data);
  }

  formatYAML(data, indent) {
    indent = indent || 0;
    const spaces = '  '.repeat(indent);
    if (data === null || data === undefined) return 'null';
    if (typeof data !== 'object') return String(data);
    if (Array.isArray(data)) {
      return data.map(item => spaces + '- ' + this.formatYAML(item, indent + 1).trim()).join('\n');
    }
    return Object.entries(data).map(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        return spaces + key + ':\n' + this.formatYAML(value, indent + 1);
      }
      return spaces + key + ': ' + value;
    }).join('\n');
  }

  formatCSV(data) {
    if (!Array.isArray(data) || data.length === 0) {
      return typeof data === 'object' ? this.formatCSV([data]) : String(data);
    }
    const headers = Object.keys(data[0] || {});
    const lines = [headers.join(',')];
    for (const row of data) {
      const values = headers.map(h => {
        const val = row[h];
        if (val === null || val === undefined) return '';
        if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
          return '"' + val.replace(/"/g, '""') + '"';
        }
        return String(val);
      });
      lines.push(values.join(','));
    }
    return lines.join('\n');
  }

  formatText(data) {
    if (typeof data === 'string') return data;
    if (typeof data === 'number' || typeof data === 'boolean') return String(data);
    if (Array.isArray(data)) return data.map(item => this.formatText(item)).join('\n');
    if (typeof data === 'object') {
      return Object.entries(data).map(([key, value]) => {
        return key + ': ' + (typeof value === 'object' ? JSON.stringify(value) : String(value));
      }).join('\n');
    }
    return String(data);
  }

  formatHTML(data) {
    if (typeof data !== 'object' || data === null) {
      return '<div>' + String(data) + '</div>';
    }
    const buildHTML = (obj) => {
      if (obj === null || obj === undefined) return '';
      if (typeof obj !== 'object') return String(obj);
      if (Array.isArray(obj)) return obj.map(item => buildHTML(item)).join('');
      let html = '';
      for (const [key, value] of Object.entries(obj)) {
        const tag = key.replace(/_/g, '-');
        html += `<${tag}>${buildHTML(value)}</${tag}>`;
      }
      return html;
    };
    return '<div class="output">' + buildHTML(data) + '</div>';
  }

  formatMarkdown(data) {
    if (typeof data === 'string') return data;
    if (typeof data !== 'object' || data === null) return String(data);
    if (Array.isArray(data) && data.length > 0 && typeof data[0] === 'object') {
      const headers = Object.keys(data[0]);
      let md = '| ' + headers.join(' | ') + ' |\n';
      md += '|' + headers.map(() => '---').join('|') + '|\n';
      for (const row of data) {
        md += '| ' + headers.map(h => String(row[h] || '')).join(' | ') + ' |\n';
      }
      return md;
    }
    return Object.entries(data).map(([key, value]) => {
      if (typeof value === 'object') return `## ${key}\n${this.formatMarkdown(value)}`;
      return `- **${key}**: ${value}`;
    }).join('\n');
  }

  formatTemplate(data, template) {
    let result = template;
    const replaceAll = (str, obj, prefix) => {
      prefix = prefix || '';
      for (const [key, value] of Object.entries(obj)) {
        const placeholder = '{{' + prefix + key + '}}';
        if (typeof value === 'object' && value !== null) {
          result = replaceAll(result, value, prefix + key + '.');
        } else {
          result = result.split(placeholder).join(String(value));
        }
      }
      return str;
    };
    result = replaceAll(result, data);
    return result;
  }

  formatBase64(data) {
    const str = typeof data === 'string' ? data : JSON.stringify(data);
    return Buffer.from(str, 'utf-8').toString('base64');
  }

  async attemptFix(error) {
    const strategies = this.config.autoFixStrategies || ['retry'];
    for (const strategy of strategies) {
      try {
        const result = await this.applyFix(strategy, error);
        if (result.success) return result;
      } catch (e) { continue; }
    }
    return null;
  }

  async applyFix(strategy, error) {
    if (strategy === 'retry') {
      // 使用JSON格式
      this.inputs.format = 'json';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[output] 自动修复成功(retry, JSON格式)'] };
    }
    if (strategy === 'text_fallback') {
      // 回退到纯文本格式
      this.inputs.format = 'text';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[output] 自动修复成功(回退到文本格式)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('format') || error.message.includes('格式')) return 'FORMAT_ERROR';
    if (error.message.includes('template') || error.message.includes('模板')) return 'TEMPLATE_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Output处理器启动');
  const handlerInstance = new OutputHandler({
    inputs: input,
    name: 'output',
    requiredInputs: ['result'],
    autoFixStrategies: ['retry', 'text_fallback']
  });
  return await handlerInstance.execute();
}

module.exports = OutputHandler;
