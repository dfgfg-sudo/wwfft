/**
 * 图片生成处理器
 * 根据文本提示词生成图片，支持多种尺寸和风格
 */

class ImageGenHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[image_gen] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[image_gen] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['prompt'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.prompt !== 'string' || this.inputs.prompt.trim() === '') {
      throw new Error('参数 prompt 不能为空字符串');
    }
  }

  async process() {
    const prompt = this.inputs.prompt;
    const size = this.inputs.size || '1024x1024';
    const style = this.inputs.style || 'natural';
    const quality = this.inputs.quality || 'standard';
    const count = this.inputs.count || 1;
    const negativePrompt = this.inputs.negative_prompt || '';
    const seed = this.inputs.seed;

    // 解析尺寸
    const dimensions = this.parseSize(size);

    // 验证参数
    const validatedParams = this.validateParams({
      prompt, size, style, quality, count, negativePrompt, seed, dimensions
    });

    // 调用图片生成API（模拟）
    const generatedImages = [];
    for (let i = 0; i < validatedParams.count; i++) {
      const image = await this.generateImage(validatedParams, i);
      generatedImages.push(image);
    }

    return {
      prompt: prompt,
      images: generatedImages,
      image_count: generatedImages.length,
      parameters: {
        size: validatedParams.size,
        style: validatedParams.style,
        quality: validatedParams.quality,
        negative_prompt: validatedParams.negativePrompt,
        seed: validatedParams.seed
      },
      dimensions: dimensions,
      executed: true
    };
  }

  parseSize(size) {
    if (typeof size === 'string') {
      const match = size.match(/(\d+)x(\d+)/);
      if (match) {
        return { width: parseInt(match[1], 10), height: parseInt(match[2], 10) };
      }
      // 预设尺寸
      const presets = {
        'square': { width: 1024, height: 1024 },
        'portrait': { width: 768, height: 1024 },
        'landscape': { width: 1024, height: 768 },
        'thumbnail': { width: 256, height: 256 },
        'hd': { width: 1920, height: 1080 }
      };
      if (presets[size]) return presets[size];
    }
    if (typeof size === 'object' && size.width && size.height) {
      return { width: size.width, height: size.height };
    }
    return { width: 1024, height: 1024 };
  }

  validateParams(params) {
    const validated = { ...params };

    // 验证prompt长度
    if (validated.prompt.length > 1000) {
      validated.prompt = validated.prompt.substring(0, 1000);
    }

    // 验证count
    validated.count = Math.max(1, Math.min(validated.count, 10));

    // 验证style
    const validStyles = ['natural', 'vivid', 'anime', 'photorealistic', 'digital-art', 'oil-painting', 'watercolor', '3d-render'];
    if (!validStyles.includes(validated.style)) {
      validated.style = 'natural';
    }

    // 验证quality
    const validQualities = ['standard', 'hd', 'ultra'];
    if (!validQualities.includes(validated.quality)) {
      validated.quality = 'standard';
    }

    // 验证尺寸范围
    const maxSize = 2048;
    if (validated.dimensions.width > maxSize || validated.dimensions.height > maxSize) {
      validated.dimensions.width = Math.min(validated.dimensions.width, maxSize);
      validated.dimensions.height = Math.min(validated.dimensions.height, maxSize);
    }

    return validated;
  }

  async generateImage(params, index) {
    await new Promise(resolve => setTimeout(resolve, 100));

    // 模拟生成的图片
    const imageId = 'img_' + Date.now() + '_' + index;
    const format = 'png';

    // 生成模拟URL
    const imageUrl = 'https://cdn.example.com/generated/' + imageId + '.' + format;

    return {
      id: imageId,
      url: imageUrl,
      format: format,
      width: params.dimensions.width,
      height: params.dimensions.height,
      style: params.style,
      quality: params.quality,
      seed: params.seed !== undefined ? params.seed + index : Math.floor(Math.random() * 1000000),
      index: index,
      size_bytes: Math.floor(params.dimensions.width * params.dimensions.height * 3 * 0.5),
      revised_prompt: params.prompt
    };
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
      // 使用默认参数重试
      this.inputs.size = '1024x1024';
      this.inputs.style = 'natural';
      this.inputs.quality = 'standard';
      this.inputs.count = 1;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[image_gen] 自动修复成功(retry, 默认参数)'] };
    }
    if (strategy === 'reduce_size') {
      // 降低分辨率
      this.inputs.size = '512x512';
      this.inputs.quality = 'standard';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[image_gen] 自动修复成功(降低分辨率)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('prompt') || error.message.includes('提示词')) return 'PROMPT_ERROR';
    if (error.message.includes('size') || error.message.includes('尺寸')) return 'SIZE_ERROR';
    if (error.message.includes('quota') || error.message.includes('limit')) return 'QUOTA_EXCEEDED';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('ImageGen处理器启动');
  const handlerInstance = new ImageGenHandler({
    inputs: input,
    name: 'image_gen',
    requiredInputs: ['prompt'],
    autoFixStrategies: ['retry', 'reduce_size']
  });
  return await handlerInstance.execute();
}

module.exports = ImageGenHandler;
