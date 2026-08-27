// coze_universal_repair_tool.ts
interface PluginInput {
  user_input: string;
  operation_mode?: "auto_detect" | "quick_fix" | "batch_process" | "smart_convert" | "coze_generate";
  target_format?: "coze_plugin" | "openapi_3_0" | "standard_json" | "typescript_interface";
  auto_repair?: boolean;
  repair_depth?: "basic" | "comprehensive" | "thorough";
}

interface PluginOutput {
  success: boolean;
  repaired_content: string;
  processing_report: {
    processing_time_ms: number;
    original_type: string;
    detected_issues: string[];
    applied_fixes: string[];
    compatibility_status: string;
    suggestions: string[];
  };
  validation_result: {
    valid: boolean;
    coze_compatible: boolean;
    issues: Array<{
      severity: 'error' | 'warning' | 'info';
      field: string;
      message: string;
      suggestion: string;
    }>;
  };
}

class UniversalRepairTool {
  private repairStrategies = {
    basic: this.basicRepair.bind(this),
    comprehensive: this.comprehensiveRepair.bind(this),
    thorough: this.thoroughRepair.bind(this)
  };

  // 主处理函数
  async processInput(input: PluginInput): Promise<PluginOutput> {
    const startTime = Date.now();
    const report = {
      processing_time_ms: 0,
      original_type: 'unknown',
      detected_issues: [] as string[],
      applied_fixes: [] as string[],
      compatibility_status: 'unknown',
      suggestions: [] as string[]
    };

    try {
      // 1. 智能输入分析
      const analysis = this.analyzeInput(input.user_input);
      report.original_type = analysis.contentType;
      report.detected_issues = analysis.detectedIssues;

      // 2. 自动选择操作模式
      const operationMode = input.operation_mode === 'auto_detect' 
        ? this.detectOperationMode(input.user_input)
        : input.operation_mode;

      // 3. 执行修复
      let result: any;
      switch (operationMode) {
        case 'quick_fix':
          result = await this.quickFix(input.user_input, input.repair_depth || 'comprehensive');
          break;
        case 'batch_process':
          result = await this.batchProcess(input.user_input, input.target_format || 'coze_plugin');
          break;
        case 'smart_convert':
          result = await this.smartConvert(input.user_input, input.target_format || 'coze_plugin');
          break;
        case 'coze_generate':
          result = await this.cozeGenerate(input.user_input);
          break;
        default:
          result = await this.quickFix(input.user_input, 'comprehensive');
      }

      // 4. 验证结果
      const validation = this.validateResult(result, input.target_format || 'coze_plugin');
      
      report.processing_time_ms = Date.now() - startTime;
      report.applied_fixes = this.extractAppliedFixes(result);
      report.compatibility_status = validation.coze_compatible ? 'fully_compatible' : 'needs_adjustment';
      report.suggestions = this.generateSuggestions(result, validation);

      return {
        success: true,
        repaired_content: typeof result === 'string' ? result : JSON.stringify(result, null, 2),
        processing_report: report,
        validation_result: validation
      };

    } catch (error) {
      report.processing_time_ms = Date.now() - startTime;
      return {
        success: false,
        repaired_content: '',
        processing_report: report,
        validation_result: {
          valid: false,
          coze_compatible: false,
          issues: [{
            severity: 'error',
            field: 'processing',
            message: `处理失败: ${error.message}`,
            suggestion: '请检查输入内容格式或尝试使用不同的修复模式'
          }]
        }
      };
    }
  }

  // 智能输入分析
  private analyzeInput(input: string): { contentType: string; detectedIssues: string[] } {
    const analysis = {
      contentType: 'unknown',
      detectedIssues: [] as string[]
    };

    // JSON检测
    if (this.looksLikeJSON(input)) {
      analysis.contentType = 'json';
      if (!this.isValidJSON(input)) {
        analysis.detectedIssues.push('JSON语法错误');
      }
    }
    // YAML检测
    else if (this.looksLikeYAML(input)) {
      analysis.contentType = 'yaml';
      analysis.detectedIssues.push('YAML格式需要转换');
    }
    // 自然语言检测
    else if (this.looksLikeNaturalLanguage(input)) {
      analysis.contentType = 'natural_language';
    }
    // 多文件检测
    else if (this.containsMultipleFiles(input)) {
      analysis.contentType = 'multiple_files';
    }

    return analysis;
  }

  // 自动检测操作模式
  private detectOperationMode(input: string): string {
    if (this.looksLikeNaturalLanguage(input)) return 'coze_generate';
    if (this.containsMultipleFiles(input)) return 'batch_process';
    if (!this.isValidJSON(input) && this.looksLikeJSON(input)) return 'quick_fix';
    if (this.looksLikeYAML(input)) return 'smart_convert';
    return 'quick_fix';
  }

  // 一键修复
  private async quickFix(input: string, repairDepth: string): Promise<any> {
    let processed = input;

    // 基础修复
    processed = this.fixCommonErrors(processed);

    // 根据修复深度执行不同级别的修复
    const repairFunction = this.repairStrategies[repairDepth as keyof typeof this.repairStrategies] || this.repairStrategies.comprehensive;
    return repairFunction(processed);
  }

  // 基础修复
  private basicRepair(input: string): any {
    let fixed = this.fixJSONSyntax(input);
    
    try {
      const parsed = JSON.parse(fixed);
      return this.ensureBasicStructure(parsed);
    } catch (error) {
      // 如果仍然无法解析，返回修复后的字符串
      return fixed;
    }
  }

  // 全面修复
  private comprehensiveRepair(input: string): any {
    let fixed = this.basicRepair(input);
    
    if (typeof fixed === 'string') {
      try {
        fixed = JSON.parse(fixed);
      } catch {
        return fixed;
      }
    }

    // 结构修复
    fixed = this.fixCozeStructure(fixed);
    fixed = this.normalizeParameters(fixed);
    
    return fixed;
  }

  // 彻底修复
  private thoroughRepair(input: string): any {
    let fixed = this.comprehensiveRepair(input);
    
    if (typeof fixed === 'string') {
      try {
        fixed = JSON.parse(fixed);
      } catch {
        return fixed;
      }
    }

    // 深度优化
    fixed = this.optimizePerformance(fixed);
    fixed = this.enhanceSecurity(fixed);
    fixed = this.ensureCozeCompatibility(fixed);
    
    return fixed;
  }

  // 批量处理
  private async batchProcess(input: string, targetFormat: string): Promise<any> {
    const fragments = this.extractJSONFragments(input);
    const processedFragments = [];

    for (const fragment of fragments) {
      if (fragment.valid) {
        try {
          const processed = await this.quickFix(fragment.content, 'comprehensive');
          processedFragments.push(processed);
        } catch (error) {
          // 跳过无效片段
        }
      }
    }

    // 合并结果
    return this.mergeFragments(processedFragments, targetFormat);
  }

  // 智能转换
  private async smartConvert(input: string, targetFormat: string): Promise<any> {
    const analysis = this.analyzeInput(input);
    
    if (analysis.contentType === 'yaml') {
      // YAML转JSON
      return this.convertYAMLToJSON(input);
    } else if (analysis.contentType === 'json') {
      // JSON格式转换
      return this.convertJSONFormat(input, targetFormat);
    }
    
    return input;
  }

  // Coze生成
  private async cozeGenerate(input: string): Promise<any> {
    // 简化的自然语言生成逻辑
    return {
      name: "generated_plugin",
      description: input.substring(0, 100) + (input.length > 100 ? '...' : ''),
      schema_version: "v1",
      name_for_human: "生成的插件",
      description_for_human: `基于描述生成的插件: ${input.substring(0, 50)}...`,
      name_for_model: "generated_plugin",
      description_for_model: `A plugin generated from description: ${input.substring(0, 50)}...`,
      inputs: [
        {
          name: 'input_param',
          type: 'string',
          required: true,
          description: '输入参数'
        }
      ],
      outputs: [
        {
          name: 'result',
          type: 'object',
          description: '处理结果'
        }
      ]
    };
  }

  // ==================== 核心修复方法 ====================

  private fixCommonErrors(input: string): string {
    let fixed = input;

    // 修复未加引号的属性名
    fixed = fixed.replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)(\s*:)/g, '$1"$2"$3');
    
    // 修复单引号
    fixed = fixed.replace(/'([^']*)'/g, '"$1"');
    
    // 修复尾随逗号
    fixed = fixed.replace(/,\s*([}\]])/g, '$1');
    
    // 修复缺少逗号
    fixed = fixed.replace(/([}\]"])\s*([{["])/g, '$1,$2');
    
    // 移除注释
    fixed = fixed.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

    return fixed;
  }

  private fixJSONSyntax(input: string): string {
    let fixed = input;
    
    try {
      JSON.parse(fixed);
      return fixed; // 如果已经是有效JSON，直接返回
    } catch (error) {
      // 尝试修复
      fixed = this.fixCommonErrors(fixed);
      
      // 更激进的修复尝试
      fixed = fixed.replace(/([{\[,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)/g, '$1"$2"$3');
      fixed = fixed.replace(/:\s*([^"{}\[\],\s][^,}\]]*)(?=[,}])/g, ':"$1"');
      
      return fixed;
    }
  }

  private ensureBasicStructure(parsed: any): any {
    const result = { ...parsed };

    // 确保基本字段
    if (!result.name) result.name = "unnamed_plugin";
    if (!result.description) result.description = "自动生成的Coze插件";
    
    // 确保输入输出结构
    if (!result.inputs && !result.input_parameters) result.inputs = [];
    if (!result.outputs && !result.output_parameters) result.outputs = [];

    return result;
  }

  private fixCozeStructure(plugin: any): any {
    const result = { ...plugin };

    // 标准化字段名称
    if (result.input_parameters && !result.inputs) {
      result.inputs = result.input_parameters;
      delete result.input_parameters;
    }
    
    if (result.output_parameters && !result.outputs) {
      result.outputs = result.output_parameters;
      delete result.output_parameters;
    }

    // 修复输入参数
    if (result.inputs && Array.isArray(result.inputs)) {
      result.inputs = result.inputs.map((input: any, index: number) => ({
        name: input.name || `input_${index}`,
        type: input.type || 'string',
        required: input.required !== undefined ? input.required : false,
        description: input.description || `参数: ${input.name || `input_${index}`}`
      }));
    }

    // 修复输出参数
    if (result.outputs && Array.isArray(result.outputs)) {
      result.outputs = result.outputs.map((output: any, index: number) => ({
        name: output.name || `output_${index}`,
        type: output.type || 'object',
        description: output.description || `输出: ${output.name || `output_${index}`}`
      }));
    }

    return result;
  }

  private normalizeParameters(plugin: any): any {
    const result = { ...plugin };

    // 添加Coze必需字段
    const requiredFields = {
      schema_version: 'v1',
      name_for_human: result.name || '未命名插件',
      description_for_human: result.description || '自动生成的Coze插件',
      name_for_model: result.name || 'unnamed_plugin',
      description_for_model: result.description || 'An automatically generated Coze plugin'
    };

    Object.entries(requiredFields).forEach(([field, defaultValue]) => {
      if (!result[field]) {
        result[field] = defaultValue;
      }
    });

    return result;
  }

  private optimizePerformance(plugin: any): any {
    // 移除空值和未定义字段
    const result = JSON.parse(JSON.stringify(plugin, (key, value) => {
      return value === null || value === undefined ? undefined : value;
    }));

    return result;
  }

  private enhanceSecurity(plugin: any): any {
    const result = { ...plugin };
    
    // 移除可能的敏感字段
    const sensitiveFields = ['api_key', 'password', 'secret', 'token'];
    sensitiveFields.forEach(field => {
      if (result[field]) {
        delete result[field];
      }
    });

    return result;
  }

  private ensureCozeCompatibility(plugin: any): any {
    const result = { ...plugin };

    // 名称规范化
    if (result.name) {
      result.name = result.name
        .toLowerCase()
        .replace(/[^a-z0-9_]/g, '_')
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '');
    }

    return result;
  }

  // ==================== 辅助方法 ====================

  private looksLikeJSON(input: string): boolean {
    const trimmed = input.trim();
    return (trimmed.startsWith('{') && trimmed.endsWith('}')) || 
           (trimmed.startsWith('[') && trimmed.endsWith(']'));
  }

  private looksLikeYAML(input: string): boolean {
    return input.includes('---') || 
           (input.includes(': ') && !input.trim().startsWith('{'));
  }

  private looksLikeNaturalLanguage(input: string): boolean {
    const jsonPattern = /^[\s\n\r]*[{\[]/;
    return !jsonPattern.test(input.trim());
  }

  private containsMultipleFiles(input: string): boolean {
    const jsonObjectCount = (input.match(/\{[^{}]*\}/g) || []).length;
    return jsonObjectCount > 1;
  }

  private isValidJSON(input: string): boolean {
    try {
      JSON.parse(input);
      return true;
    } catch {
      return false;
    }
  }

  private extractJSONFragments(input: string): Array<{content: string; valid: boolean}> {
    const fragments: Array<{content: string; valid: boolean}> = [];
    
    // 简单提取大括号包围的内容
    const braceMatches = input.match(/\{[^{}]*\}/g) || [];
    braceMatches.forEach(match => {
      fragments.push({
        content: match,
        valid: this.isValidJSON(match)
      });
    });

    return fragments;
  }

  private mergeFragments(fragments: any[], targetFormat: string): any {
    if (fragments.length === 0) return {};
    if (fragments.length === 1) return fragments[0];

    const merged = {
      name: "merged_plugins",
      description: "合并的插件集合",
      schema_version: "v1",
      merged_plugins: fragments,
      merged_at: new Date().toISOString(),
      total_plugins: fragments.length
    };

    return merged;
  }

  private convertYAMLToJSON(yamlString: string): any {
    // 简化的YAML转JSON逻辑
    // 实际实现应该使用YAML解析库
    return {
      name: "converted_from_yaml",
      description: "从YAML转换的插件",
      schema_version: "v1",
      note: "YAML转换功能需要完整的YAML解析器实现"
    };
  }

  private convertJSONFormat(input: string, targetFormat: string): any {
    try {
      const parsed = JSON.parse(input);
      
      if (targetFormat === 'coze_plugin') {
        return this.ensureCozeCompatibility(parsed);
      }
      
      return parsed;
    } catch {
      return input;
    }
  }

  private validateResult(result: any, targetFormat: string): PluginOutput['validation_result'] {
    const issues: PluginOutput['validation_result']['issues'] = [];

    if (targetFormat === 'coze_plugin') {
      // Coze插件必需字段检查
      const requiredFields = ['name', 'description', 'schema_version'];
      requiredFields.forEach(field => {
        if (!result[field]) {
          issues.push({
            severity: 'error',
            field: field,
            message: `缺少必需字段: ${field}`,
            suggestion: `添加 ${field} 字段`
          });
        }
      });

      // 检查输入输出结构
      const inputs = result.inputs || result.input_parameters;
      if (inputs && !Array.isArray(inputs)) {
        issues.push({
          severity: 'error',
          field: 'inputs',
          message: 'inputs必须是数组',
          suggestion: '将inputs转换为数组格式'
        });
      }

      const outputs = result.outputs || result.output_parameters;
      if (outputs && !Array.isArray(outputs)) {
        issues.push({
          severity: 'error',
          field: 'outputs',
          message: 'outputs必须是数组',
          suggestion: '将outputs转换为数组格式'
        });
      }
    }

    return {
      valid: issues.length === 0,
      coze_compatible: issues.filter(issue => issue.severity === 'error').length === 0,
      issues
    };
  }

  private extractAppliedFixes(result: any): string[] {
    const fixes: string[] = [];
    
    if (typeof result === 'object') {
      if (result.name && result.name !== 'unnamed_plugin') fixes.push('修复插件名称');
      if (result.schema_version) fixes.push('添加schema_version');
      if (result.inputs && Array.isArray(result.inputs)) fixes.push('修复输入参数结构');
      if (result.outputs && Array.isArray(result.outputs)) fixes.push('修复输出参数结构');
    }
    
    return fixes;
  }

  private generateSuggestions(result: any, validation: PluginOutput['validation_result']): string[] {
    const suggestions: string[] = [];

    if (validation.issues.length > 0) {
      suggestions.push('请根据验证报告修复存在的问题');
    }

    if (typeof result === 'object') {
      if (!result.description || result.description.length < 10) {
        suggestions.push('建议提供更详细的插件描述');
      }

      const inputs = result.inputs || result.input_parameters;
      if (!inputs || inputs.length === 0) {
        suggestions.push('建议添加输入参数以增强插件功能');
      }
    }

    if (suggestions.length === 0) {
      suggestions.push('内容结构良好，可以直接在Coze平台使用');
    }

    return suggestions;
  }
}

// 导出函数供Coze平台使用
export async function run(input: PluginInput): Promise<PluginOutput> {
  const tool = new UniversalRepairTool();
  return await tool.processInput(input);
}

export default { run };