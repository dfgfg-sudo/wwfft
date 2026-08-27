/**
 * 视频生成处理器
 * 根据文本提示词生成视频，支持多种时长和分辨率
 */

class VideoGenHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[video_gen] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[video_gen] 执行失败: ' + error.message] };
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
    const duration = this.inputs.duration || 5;
    const resolution = this.inputs.resolution || '720p';
    const fps = this.inputs.fps || 24;
    const style = this.inputs.style || 'cinematic';
    const aspectRatio = this.inputs.aspect_ratio || '16:9';
    const negativePrompt = this.inputs.negative_prompt || '';
    const seed = this.inputs.seed;

    // 参数验证和修正
    const validated = this.validateParams({
      prompt, duration, resolution, fps, style, aspectRatio, negativePrompt, seed
    });

    // 生成视频（模拟）
    const videoResult = await this.generateVideo(validated);

    return {
      prompt: prompt,
      video_url: videoResult.url,
      video_id: videoResult.id,
      duration: validated.duration,
      resolution: validated.resolution,
      fps: validated.fps,
      style: validated.style,
      aspect_ratio: validated.aspectRatio,
      format: videoResult.format,
      parameters: {
        negative_prompt: validated.negativePrompt,
        seed: validated.seed
      },
      metadata: {
        width: videoResult.width,
        height: videoResult.height,
        frame_count: videoResult.frameCount,
        file_size: videoResult.fileSize,
        codec: videoResult.codec,
        bitrate: videoResult.bitrate
      },
      processing_info: {
        processing_time_ms: videoResult.processingTime,
        model_used: videoResult.model
      },
      executed: true
    };
  }

  validateParams(params) {
    const validated = { ...params };

    // 验证prompt长度
    if (validated.prompt.length > 2000) {
      validated.prompt = validated.prompt.substring(0, 2000);
    }

    // 验证时长
    validated.duration = Math.max(1, Math.min(validated.duration, 60));

    // 验证分辨率
    const validResolutions = ['480p', '720p', '1080p', '1440p', '4k'];
    if (!validResolutions.includes(validated.resolution)) {
      validated.resolution = '720p';
    }

    // 验证FPS
    validated.fps = Math.max(1, Math.min(validated.fps, 60));

    // 验证风格
    const validStyles = ['cinematic', 'anime', 'realistic', 'cartoon', '3d', 'artistic'];
    if (!validStyles.includes(validated.style)) {
      validated.style = 'cinematic';
    }

    // 验证宽高比
    const validRatios = ['16:9', '9:16', '1:1', '4:3', '21:9'];
    if (!validRatios.includes(validated.aspectRatio)) {
      validated.aspectRatio = '16:9';
    }

    return validated;
  }

  async generateVideo(params) {
    await new Promise(resolve => setTimeout(resolve, 200));

    const resolutionMap = {
      '480p': { width: 854, height: 480 },
      '720p': { width: 1280, height: 720 },
      '1080p': { width: 1920, height: 1080 },
      '1440p': { width: 2560, height: 1440 },
      '4k': { width: 3840, height: 2160 }
    };

    const dims = resolutionMap[params.resolution] || resolutionMap['720p'];
    const frameCount = Math.ceil(params.duration * params.fps);
    const videoId = 'vid_' + Date.now();

    return {
      id: videoId,
      url: 'https://cdn.example.com/generated/' + videoId + '.mp4',
      format: 'mp4',
      width: dims.width,
      height: dims.height,
      frameCount: frameCount,
      fileSize: Math.floor(dims.width * dims.height * frameCount * 0.1),
      codec: 'H.264',
      bitrate: Math.floor(dims.width * dims.height * params.fps * 0.07),
      model: 'VideoGen-Pro-v2',
      processingTime: Math.floor(params.duration * 1000 + 500)
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
      // 使用默认参数
      this.inputs.duration = 5;
      this.inputs.resolution = '720p';
      this.inputs.fps = 24;
      this.inputs.style = 'cinematic';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[video_gen] 自动修复成功(retry, 默认参数)'] };
    }
    if (strategy === 'reduce_quality') {
      // 降低质量
      this.inputs.resolution = '480p';
      this.inputs.fps = 15;
      this.inputs.duration = Math.min(this.inputs.duration || 5, 10);
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[video_gen] 自动修复成功(降低质量)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('prompt') || error.message.includes('提示词')) return 'PROMPT_ERROR';
    if (error.message.includes('duration') || error.message.includes('时长')) return 'DURATION_ERROR';
    if (error.message.includes('resolution') || error.message.includes('分辨率')) return 'RESOLUTION_ERROR';
    if (error.message.includes('quota') || error.message.includes('limit')) return 'QUOTA_EXCEEDED';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('VideoGen处理器启动');
  const handlerInstance = new VideoGenHandler({
    inputs: input,
    name: 'video_gen',
    requiredInputs: ['prompt'],
    autoFixStrategies: ['retry', 'reduce_quality']
  });
  return await handlerInstance.execute();
}

module.exports = VideoGenHandler;
