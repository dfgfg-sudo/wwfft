const vm = require('vm');
const fs = require('fs');
const path = require('path');

class CodeExecutor {
  constructor() {
    this.context = vm.createContext({
      console: console,
      require: require,
      module: module,
      exports: exports,
      __dirname: __dirname,
      __filename: __filename,
      process: process,
      Buffer: Buffer,
      setTimeout: setTimeout,
      setInterval: setInterval,
      clearTimeout: clearTimeout,
      clearInterval: clearInterval,
      Promise: Promise,
      Array: Array,
      Object: Object,
      String: String,
      Number: Number,
      Boolean: Boolean,
      Date: Date,
      Math: Math,
      JSON: JSON,
      Error: Error,
      TypeError: TypeError,
      RangeError: RangeError
    });
    this.executedModules = {};
    this.globalScope = {};
  }

  async executePythonCode(pythonCode) {
    return new Promise((resolve) => {
      const simplifiedCode = this._extractPurePython(pythonCode);
      if (!simplifiedCode.trim()) {
        resolve({ success: false, message: '未找到可执行的Python代码' });
        return;

      try {
        const result = this._executePythonInNode(simplifiedCode);
        resolve({ success: true, result: result, code: simplifiedCode });
      } catch (error) {
        resolve({ success: false, error: error.message, code: simplifiedCode });

  _extractPurePython(code) {
    code = code.replace(/```python\s*/g, '');
    code = code.replace(/```\s*$/g, '');
    code = code.replace(/^#.*$/gm, '');
    return code.trim();

  _executePythonInNode(code) {
    const extractedClasses = this._parsePythonClasses(code);
    const extractedFunctions = this._parsePythonFunctions(code);
    
    const nodeEquivalents = {
      classes: extractedClasses,
      functions: extractedFunctions,
      rawCode: code
    };

    return nodeEquivalents;

  _parsePythonClasses(code) {
    const classPattern = /class\s+(\w+)\s*(?:\([^)]*\))?\s*:\s*([\s\S]*?)(?=\nclass|\ndef|\Z)/g;
    const classes = [];
    let match;

    while ((match = classPattern.exec(code)) !== null) {
      const className = match[1];
      const classBody = match[2].trim();
      
      const methods = this._extractMethodsFromClass(classBody);
      classes.push({
        name: className,
        methods: methods,
        rawCode: match[0]

    return classes;

  _extractMethodsFromClass(classBody) {
    const methodPattern = /def\s+(\w+)\s*\(([^)]*)\)\s*:\s*([\s\S]*?)(?=\n\s*def|\n\s*@|\Z)/g;
    const methods = [];

    while ((match = methodPattern.exec(classBody)) !== null) {
      methods.push({
        name: match[1],
        parameters: match[2].split(',').map(p => p.trim()).filter(p => p && p !== 'self'),
        body: match[3].trim()

    return methods;

  _parsePythonFunctions(code) {
    const funcPattern = /def\s+(\w+)\s*\(([^)]*)\)\s*:\s*([\s\S]*?)(?=\n\s*def|\n\s*class|\Z)/g;
    const functions = [];

    while ((match = funcPattern.exec(code)) !== null) {
      functions.push({
        parameters: match[2].split(',').map(p => p.trim()).filter(p => p),
        body: match[3].trim(),

    return functions;

  executeJavaScriptCode(jsCode) {
      const result = vm.runInContext(jsCode, this.context);
      return { success: true, result: result };
      return { success: false, error: error.message };

  loadModule(moduleName, code) {
      const moduleContext = vm.createContext({
        ...this.context,
        module: { exports: {} },
        exports: {}

      vm.runInContext(code, moduleContext);
      this.executedModules[moduleName] = moduleContext.module.exports || moduleContext.exports;
      return { success: true, module: this.executedModules[moduleName] };

  getModule(moduleName) {
    return this.executedModules[moduleName] || null;

  setGlobal(key, value) {
    this.globalScope[key] = value;
    this.context[key] = value;

  getGlobal(key) {
    return this.globalScope[key];

module.exports = CodeExecutor;