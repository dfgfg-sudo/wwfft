/**
 * 文本处理处理器
 * 对输入文本执行各种操作，如trim、replace、split、join、case转换等
 */

class TextProcessHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[text_process] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[text_process] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['text', 'operation'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.text !== 'string') {
      throw new Error('参数 text 必须是字符串');
    }
    if (typeof this.inputs.operation !== 'string') {
      throw new Error('参数 operation 必须是字符串');
    }
  }

  async process() {
    const text = this.inputs.text;
    const operation = this.inputs.operation;
    const params = this.inputs.params || {};

    let result;

    switch (operation) {
      case 'trim':
        result = text.trim();
        break;
      case 'trim_start':
      case 'trimStart':
        result = text.trimStart();
        break;
      case 'trim_end':
      case 'trimEnd':
        result = text.trimEnd();
        break;
      case 'lower':
      case 'toLowerCase':
        result = text.toLowerCase();
        break;
      case 'upper':
      case 'toUpperCase':
        result = text.toUpperCase();
        break;
      case 'capitalize':
        result = text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
        break;
      case 'title':
        result = text.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
        break;
      case 'replace':
        if (!params.search || params.replacement === undefined) {
          throw new Error('replace操作需要params.search和params.replacement参数');
        }
        const flags = params.flags || 'g';
        const regex = new RegExp(params.search, flags);
        result = text.replace(regex, params.replacement);
        break;
      case 'replace_all':
        if (!params.search || params.replacement === undefined) {
          throw new Error('replace_all操作需要params.search和params.replacement参数');
        }
        result = text.split(params.search).join(params.replacement);
        break;
      case 'split':
        if (!params.separator) {
          throw new Error('split操作需要params.separator参数');
        }
        result = text.split(params.separator);
        break;
      case 'join':
        if (!Array.isArray(text)) {
          throw new Error('join操作要求text参数是数组');
        }
        result = text.join(params.separator || '');
        break;
      case 'substring':
      case 'substr':
        const start = params.start || 0;
        const end = params.end !== undefined ? params.end : text.length;
        result = text.substring(start, end);
        break;
      case 'concat':
        if (!params.suffix) {
          throw new Error('concat操作需要params.suffix或params.prefix参数');
        }
        result = (params.prefix || '') + text + (params.suffix || '');
        break;
      case 'reverse':
        result = text.split('').reverse().join('');
        break;
      case 'pad':
        const padStr = params.pad_string || ' ';
        const padLength = params.length || text.length;
        const padSide = params.side || 'right';
        if (padSide === 'left') {
          result = text.padStart(padLength, padStr);
        } else {
          result = text.padEnd(padLength, padStr);
        }
        break;
      case 'encode':
        result = this.encode(text, params.encoding || 'base64');
        break;
      case 'decode':
        result = this.decode(text, params.encoding || 'base64');
        break;
      case 'extract_regex':
        if (!params.pattern) {
          throw new Error('extract_regex操作需要params.pattern参数');
        }
        const extractRegex = new RegExp(params.pattern, params.flags || 'g');
        const matches = [];
        let match;
        while ((match = extractRegex.exec(text)) !== null) {
          matches.push(match[0]);
        }
        result = matches;
        break;
      case 'word_count':
        result = text.trim().split(/\s+/).filter(w => w.length > 0).length;
        break;
      case 'char_count':
        result = text.length;
        break;
      case 'line_count':
        result = text.split('\n').length;
        break;
      default:
        throw new Error('不支持的操作: ' + operation);
    }

    return {
      operation: operation,
      original: text,
      result: result,
      params: params,
      executed: true
    };
  }

  encode(text, encoding) {
    switch (encoding) {
      case 'base64':
        return Buffer.from(text, 'utf-8').toString('base64');
      case 'uri':
        return encodeURIComponent(text);
      case 'html':
        return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
      default:
        return text;
    }
  }

  decode(text, encoding) {
    switch (encoding) {
      case 'base64':
        return Buffer.from(text, 'base64').toString('utf-8');
      case 'uri':
        return decodeURIComponent(text);
      case 'html':
        return text.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
      default:
        return text;
    }
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
      // 使用默认操作
      if (!this.inputs.operation) {
        this.inputs.operation = 'trim';
      }
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[text_process] 自动修复成功(retry)'] };
    }
    if (strategy === 'default_params') {
      this.inputs.params = this.inputs.params || {};
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[text_process] 自动修复成功(使用默认params)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('不支持') || error.message.includes('操作')) return 'UNSUPPORTED_OPERATION';
    if (error.message.includes('regex') || error.message.includes('正则')) return 'REGEX_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('TextProcess处理器启动');
  const handlerInstance = new TextProcessHandler({
    inputs: input,
    name: 'text_process',
    requiredInputs: ['text', 'operation'],
    autoFixStrategies: ['retry', 'default_params']
  });
  return await handlerInstance.execute();
}

module.exports = TextProcessHandler;
