/**
 * 画布处理器
 * 对画布元素进行增删改查、渲染和导出操作
 */

class CanvasHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.canvasState = {
      elements: [],
      layers: [],
      metadata: {
        width: 1920,
        height: 1080,
        background: '#ffffff',
        dpi: 72
      }
    };
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[canvas] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[canvas] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['elements'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (!Array.isArray(this.inputs.elements) && typeof this.inputs.elements !== 'object') {
      throw new Error('参数 elements 必须是数组或对象');
    }
  }

  async process() {
    const elements = Array.isArray(this.inputs.elements) ? this.inputs.elements : [this.inputs.elements];
    const operation = this.inputs.operation || 'render';
    const canvasConfig = this.inputs.canvas_config || {};

    // 合并画布配置
    Object.assign(this.canvasState.metadata, canvasConfig);

    switch (operation) {
      case 'render':
        return await this.renderCanvas(elements);
      case 'compose':
        return await this.composeElements(elements);
      case 'layout':
        return await this.autoLayout(elements);
      case 'export':
        return await this.exportCanvas(elements);
      case 'transform':
        return await this.transformElements(elements);
      case 'validate':
        return await this.validateElements(elements);
      default:
        return await this.renderCanvas(elements);
    }
  }

  async renderCanvas(elements) {
    await new Promise(resolve => setTimeout(resolve, 20));

    const renderedElements = elements.map((el, index) => {
      const element = {
        id: el.id || 'el_' + index,
        type: el.type || 'shape',
        x: el.x || 0,
        y: el.y || 0,
        width: el.width || 100,
        height: el.height || 100,
        rotation: el.rotation || 0,
        opacity: el.opacity !== undefined ? el.opacity : 1,
        visible: el.visible !== false,
        locked: el.locked || false,
        style: el.style || {},
        content: el.content || null,
        zIndex: el.zIndex !== undefined ? el.zIndex : index,
        layer: el.layer || 'layer_' + Math.floor(index / 10)
      };

      // 根据类型设置默认样式
      if (element.type === 'text') {
        element.style = {
          fontSize: 14,
          fontFamily: 'Arial',
          color: '#000000',
          textAlign: 'left',
          ...element.style
        };
      } else if (element.type === 'shape') {
        element.style = {
          fillColor: '#cccccc',
          strokeColor: '#000000',
          strokeWidth: 1,
          ...element.style
        };
      } else if (element.type === 'image') {
        element.style = {
          fit: 'contain',
          ...element.style
        };
        element.src = el.src || '';
      }

      return element;
    });

    this.canvasState.elements = renderedElements;

    return {
      operation: 'render',
      canvas: {
        width: this.canvasState.metadata.width,
        height: this.canvasState.metadata.height,
        background: this.canvasState.metadata.background
      },
      elements: renderedElements,
      element_count: renderedElements.length,
      layers: [...new Set(renderedElements.map(e => e.layer))],
      executed: true
    };
  }

  async composeElements(elements) {
    const rendered = await this.renderCanvas(elements);
    const groups = {};

    // 按layer分组
    for (const el of rendered.elements) {
      if (!groups[el.layer]) groups[el.layer] = [];
      groups[el.layer].push(el);
    }

    // 计算边界框
    const bounds = this.calculateBounds(rendered.elements);

    return {
      operation: 'compose',
      groups: groups,
      group_count: Object.keys(groups).length,
      bounds: bounds,
      elements: rendered.elements,
      executed: true
    };
  }

  async autoLayout(elements) {
    const layoutType = this.inputs.layout_type || 'grid';
    const gap = this.inputs.gap || 10;
    const cols = this.inputs.columns || 3;

    const processedElements = [...elements];

    if (layoutType === 'grid') {
      const rows = Math.ceil(processedElements.length / cols);
      const cellWidth = (this.canvasState.metadata.width - gap * (cols + 1)) / cols;
      const cellHeight = (this.canvasState.metadata.height - gap * (rows + 1)) / rows;

      processedElements.forEach((el, index) => {
        const row = Math.floor(index / cols);
        const col = index % cols;
        el.x = gap + col * (cellWidth + gap);
        el.y = gap + row * (cellHeight + gap);
        el.width = el.width || cellWidth;
        el.height = el.height || cellHeight;
      });
    } else if (layoutType === 'stack') {
      let currentY = gap;
      processedElements.forEach(el => {
        el.x = gap;
        el.y = currentY;
        el.width = el.width || (this.canvasState.metadata.width - gap * 2);
        currentY += (el.height || 100) + gap;
      });
    } else if (layoutType === 'flow') {
      let currentX = gap;
      let currentY = gap;
      let maxY = 0;
      processedElements.forEach(el => {
        const elWidth = el.width || 100;
        const elHeight = el.height || 100;
        if (currentX + elWidth > this.canvasState.metadata.width - gap) {
          currentX = gap;
          currentY += maxY + gap;
          maxY = 0;
        }
        el.x = currentX;
        el.y = currentY;
        currentX += elWidth + gap;
        maxY = Math.max(maxY, elHeight);
      });
    }

    return {
      operation: 'layout',
      layout_type: layoutType,
      elements: processedElements,
      element_count: processedElements.length,
      executed: true
    };
  }

  async exportCanvas(elements) {
    const format = this.inputs.export_format || 'json';
    const rendered = await this.renderCanvas(elements);

    let exported;
    switch (format) {
      case 'json':
        exported = JSON.stringify(rendered, null, 2);
        break;
      case 'svg':
        exported = this.toSVG(rendered.elements);
        break;
      case 'html':
        exported = this.toHTML(rendered.elements);
        break;
      default:
        exported = JSON.stringify(rendered, null, 2);
    }

    return {
      operation: 'export',
      format: format,
      data: exported,
      size: exported.length,
      element_count: rendered.elements.length,
      executed: true
    };
  }

  async transformElements(elements) {
    const transform = this.inputs.transform || {};
    const { translate_x = 0, translate_y = 0, scale = 1, rotate = 0 } = transform;

    const transformed = elements.map(el => ({
      ...el,
      x: (el.x || 0) + translate_x,
      y: (el.y || 0) + translate_y,
      width: (el.width || 100) * scale,
      height: (el.height || 100) * scale,
      rotation: (el.rotation || 0) + rotate
    }));

    return {
      operation: 'transform',
      transform: { translate_x, translate_y, scale, rotate },
      elements: transformed,
      executed: true
    };
  }

  async validateElements(elements) {
    const errors = [];
    const warnings = [];

    elements.forEach((el, index) => {
      if (!el.type) warnings.push({ index, message: '元素缺少type属性' });
      if (el.x !== undefined && el.x < 0) errors.push({ index, message: 'x坐标不能为负数' });
      if (el.y !== undefined && el.y < 0) errors.push({ index, message: 'y坐标不能为负数' });
      if (el.width !== undefined && el.width <= 0) errors.push({ index, message: '宽度必须大于0' });
      if (el.height !== undefined && el.height <= 0) errors.push({ index, message: '高度必须大于0' });
      if (el.opacity !== undefined && (el.opacity < 0 || el.opacity > 1)) {
        warnings.push({ index, message: '透明度应在0-1之间' });
      }
    });

    return {
      operation: 'validate',
      valid: errors.length === 0,
      errors: errors,
      warnings: warnings,
      element_count: elements.length,
      executed: true
    };
  }

  calculateBounds(elements) {
    if (elements.length === 0) return { x: 0, y: 0, width: 0, height: 0 };
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const el of elements) {
      minX = Math.min(minX, el.x || 0);
      minY = Math.min(minY, el.y || 0);
      maxX = Math.max(maxX, (el.x || 0) + (el.width || 0));
      maxY = Math.max(maxY, (el.y || 0) + (el.height || 0));
    }
    return { x: minX, y: minY, width: maxX - minX, height: maxY - minY };
  }

  toSVG(elements) {
    let svg = `<svg width="${this.canvasState.metadata.width}" height="${this.canvasState.metadata.height}" xmlns="http://www.w3.org/2000/svg">`;
    for (const el of elements) {
      if (el.type === 'shape') {
        svg += `<rect x="${el.x}" y="${el.y}" width="${el.width}" height="${el.height}" fill="${el.style?.fillColor || '#ccc'}" stroke="${el.style?.strokeColor || '#000'}" stroke-width="${el.style?.strokeWidth || 1}" />`;
      } else if (el.type === 'text' && el.content) {
        svg += `<text x="${el.x}" y="${el.y}" font-size="${el.style?.fontSize || 14}" fill="${el.style?.color || '#000'}">${el.content}</text>`;
      }
    }
    svg += '</svg>';
    return svg;
  }

  toHTML(elements) {
    let html = `<div style="position:relative;width:${this.canvasState.metadata.width}px;height:${this.canvasState.metadata.height}px;background:${this.canvasState.metadata.background}">`;
    for (const el of elements) {
      html += `<div style="position:absolute;left:${el.x}px;top:${el.y}px;width:${el.width}px;height:${el.height}px;opacity:${el.opacity}">${el.content || ''}</div>`;
    }
    html += '</div>';
    return html;
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
      // 使用默认render操作
      this.inputs.operation = 'render';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[canvas] 自动修复成功(retry, render模式)'] };
    }
    if (strategy === 'auto_fix_elements') {
      // 修复元素属性
      this.inputs.elements = this.inputs.elements.map(el => ({
        ...el,
        x: Math.max(0, el.x || 0),
        y: Math.max(0, el.y || 0),
        width: Math.max(1, el.width || 100),
        height: Math.max(1, el.height || 100),
        opacity: Math.max(0, Math.min(1, el.opacity !== undefined ? el.opacity : 1))
      }));
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[canvas] 自动修复成功(修复元素属性)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('element') || error.message.includes('元素')) return 'ELEMENT_ERROR';
    if (error.message.includes('canvas') || error.message.includes('画布')) return 'CANVAS_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Canvas处理器启动');
  const handlerInstance = new CanvasHandler({
    inputs: input,
    name: 'canvas',
    requiredInputs: ['elements'],
    autoFixStrategies: ['retry', 'auto_fix_elements']
  });
  return await handlerInstance.execute();
}

module.exports = CanvasHandler;
