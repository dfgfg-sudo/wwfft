/**
 * ============================================================================
 * Coze Plugin Code Generator - Fixed Version
 * ============================================================================
 * Description:    A robust plugin code generator for the Coze platform.
 *                  Converts TypeScript concepts to CommonJS (CJS) JavaScript,
 *                  includes full JSON Schema metadata, input validation,
 *                  and generates complete plugin code templates with configs.
 * Version:        2.0.0-fixed
 * Format:         CommonJS (CJS)
 * Encoding:       UTF-8
 * ============================================================================
 */

'use strict';

// -----------------------------------------------------------------------------
// JSON Schema Metadata Definitions
// -----------------------------------------------------------------------------

/**
 * Input parameter schema for the handler function.
 * Defines the structure and validation rules for incoming requests.
 */
const INPUT_SCHEMA = {
  type: 'object',
  required: ['plugin_requirement'],
  additionalProperties: true,
  properties: {
    plugin_requirement: {
      type: 'string',
      description: 'Detailed description of the plugin functionality to be generated.',
      minLength: 1,
      maxLength: 5000
    },
    request: {
      type: 'string',
      description: 'Optional fallback parameter field for plugin requirements.',
      minLength: 0,
      maxLength: 5000,
      default: ''
    },
    query: {
      type: 'string',
      description: 'Optional fallback parameter field for plugin queries.',
      minLength: 0,
      maxLength: 5000,
      default: ''
    }
  }
};

/**
 * Output response schema for the handler function.
 * Defines the structure of the successful response data.
 */
const OUTPUT_SCHEMA = {
  type: 'object',
  required: ['code', 'message', 'data'],
  properties: {
    code: {
      type: 'integer',
      description: 'Status code. 0 indicates success, non-zero indicates failure.',
      enum: [0, 400, 500]
    },
    message: {
      type: 'string',
      description: 'Human-readable status message.'
    },
    data: {
      type: 'object',
      description: 'Payload containing generated plugin artifacts.',
      required: ['pluginName', 'pluginDescription', 'code', 'config', 'usageInstructions', 'generationTime'],
      properties: {
        pluginName: {
          type: 'string',
          description: 'Normalized name of the generated plugin.'
        },
        pluginDescription: {
          type: 'string',
          description: 'Short description of the generated plugin.'
        },
        code: {
          type: 'string',
          description: 'Complete JavaScript plugin source code (CJS format).'
        },
        config: {
          type: 'object',
          description: 'Structured plugin configuration object.'
        },
        usageInstructions: {
          type: 'string',
          description: 'Step-by-step usage guide for the generated plugin.'
        },
        generationTime: {
          type: 'string',
          description: 'ISO 8601 timestamp of when the plugin was generated.',
          format: 'date-time'
        }
      }
    }
  }
};

/**
 * Complete plugin metadata exported for platform registration.
 */
const PLUGIN_METADATA = {
  name: 'coze-plugin-code-generator',
  version: '2.0.0-fixed',
  description: 'Generates complete Coze plugin code, configuration, and usage instructions from natural language requirements.',
  author: 'System',
  license: 'MIT',
  inputSchema: INPUT_SCHEMA,
  outputSchema: OUTPUT_SCHEMA,
  runtime: 'node',
  moduleFormat: 'commonjs'
};

// -----------------------------------------------------------------------------
// Validation Utilities
// -----------------------------------------------------------------------------

/**
 * Validates a value against a JSON Schema subset.
 * Supports: type, required, minLength, maxLength, enum, properties.
 *
 * @param {any} value       - The value to validate.
 * @param {object} schema   - The JSON Schema object.
 * @param {string} path     - Current property path for error messages.
 * @returns {{valid: boolean, errors: string[]}}
 */
function validateSchema(value, schema, path = 'root') {
  const errors = [];

  if (schema === null || typeof schema !== 'object') {
    return { valid: true, errors };
  }

  // Type check
  if (schema.type) {
    const actualType = Array.isArray(value) ? 'array' : typeof value;
    if (schema.type === 'integer') {
      if (typeof value !== 'number' || !Number.isInteger(value)) {
        errors.push(`[${path}] Expected integer, got ${actualType}.`);
      }
    } else if (schema.type === 'array') {
      if (!Array.isArray(value)) {
        errors.push(`[${path}] Expected array, got ${actualType}.`);
      }
    } else if (schema.type !== actualType) {
      errors.push(`[${path}] Expected type "${schema.type}", got "${actualType}".`);
    }
  }

  // String length checks
  if (typeof value === 'string') {
    if (schema.minLength !== undefined && value.length < schema.minLength) {
      errors.push(`[${path}] String length ${value.length} is less than minimum ${schema.minLength}.`);
    }
    if (schema.maxLength !== undefined && value.length > schema.maxLength) {
      errors.push(`[${path}] String length ${value.length} exceeds maximum ${schema.maxLength}.`);
    }
  }

  // Enum check
  if (schema.enum && !schema.enum.includes(value)) {
    errors.push(`[${path}] Value must be one of [${schema.enum.join(', ')}], got "${value}".`);
  }

  // Object property checks
  if (schema.type === 'object' && value !== null && typeof value === 'object' && !Array.isArray(value)) {
    if (schema.required && Array.isArray(schema.required)) {
      for (const key of schema.required) {
        if (!(key in value)) {
          errors.push(`[${path}] Missing required property "${key}".`);
        }
      }
    }

    if (schema.properties && typeof schema.properties === 'object') {
      for (const [key, propSchema] of Object.entries(schema.properties)) {
        if (key in value) {
          const result = validateSchema(value[key], propSchema, `${path}.${key}`);
          errors.push(...result.errors);
        }
      }
    }
  }

  return { valid: errors.length === 0, errors };
}

// -----------------------------------------------------------------------------
// Helper Utilities
// -----------------------------------------------------------------------------

/**
 * Normalizes a requirement string by extracting the primary description.
 * Falls back to alternative fields if the primary field is empty.
 *
 * @param {object} params - Input parameters.
 * @returns {string} - Normalized requirement string.
 */
function normalizeRequirement(params) {
  if (!params || typeof params !== 'object') {
    return '';
  }

  const primary = typeof params.plugin_requirement === 'string'
    ? params.plugin_requirement.trim()
    : '';

  if (primary.length > 0) {
    return primary;
  }

  const fallback = typeof params.request === 'string'
    ? params.request.trim()
    : (typeof params.query === 'string' ? params.query.trim() : '');

  return fallback;
}

/**
 * Converts a requirement string into a valid plugin identifier (camelCase).
 *
 * @param {string} requirement - Raw requirement text.
 * @returns {string} - Valid plugin identifier.
 */
function toPluginIdentifier(requirement) {
  if (!requirement || typeof requirement !== 'string') {
    return 'generatedPlugin';
  }

  const cleaned = requirement
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .trim();

  const words = cleaned.split(/\s+/).filter(Boolean);
  if (words.length === 0) {
    return 'generatedPlugin';
  }

  const first = words[0];
  const rest = words.slice(1).map(w => w.charAt(0).toUpperCase() + w.slice(1));
  const identifier = first + rest.join('');

  // Ensure it starts with a letter
  if (/^[0-9]/.test(identifier)) {
    return 'plugin' + identifier.charAt(0).toUpperCase() + identifier.slice(1);
  }

  return identifier;
}

/**
 * Generates a short plugin description from the requirement.
 *
 * @param {string} requirement - Raw requirement text.
 * @returns {string} - Short description.
 */
function toPluginDescription(requirement) {
  if (!requirement || typeof requirement !== 'string') {
    return 'Auto-generated Coze plugin.';
  }
  const trimmed = requirement.trim();
  if (trimmed.length <= 120) {
    return trimmed;
  }
  return trimmed.substring(0, 117) + '...';
}

// -----------------------------------------------------------------------------
// Core Generation Functions
// -----------------------------------------------------------------------------

/**
 * Generates a complete plugin code template in CommonJS format.
 *
 * @param {string} requirement - Plugin requirement description.
 * @returns {string} - Generated JavaScript source code.
 */
function generatePluginCode(requirement) {
  if (!requirement || typeof requirement !== 'string') {
    requirement = 'Default plugin functionality';
  }

  const pluginName = toPluginIdentifier(requirement);
  const pluginDesc = toPluginDescription(requirement);

  const code = `'use strict';

/**
 * Coze Plugin: ${pluginName}
 * Description: ${pluginDesc}
 * Auto-generated by Coze Plugin Code Generator
 */

/**
 * Main handler function for the plugin.
 *
 * @param {object} params - Input parameters from the Coze platform.
 * @returns {object} - Response object conforming to the Coze plugin protocol.
 */
async function handler(params) {
  try {
    // Validate input presence
    if (!params || typeof params !== 'object') {
      return {
        code: 400,
        message: 'Invalid input: params must be a non-null object.',
        data: null
      };
    }

    // Extract primary input fields
    const input = params.input || params.query || params.request || '';

    // -------------------------------------------------------------------------
    // TODO: Implement your custom plugin logic here based on the requirement:
    // "${requirement.replace(/"/g, '\\"')}"
    // -------------------------------------------------------------------------

    const result = {
      processedInput: input,
      timestamp: new Date().toISOString(),
      pluginName: '${pluginName}'
    };

    return {
      code: 0,
      message: 'Success',
      data: result
    };
  } catch (error) {
    return {
      code: 500,
      message: `Internal error: \${error.message}`,
      data: null
    };
  }
}

module.exports = { handler };
`;

  return code;
}

/**
 * Generates a structured plugin configuration object.
 *
 * @param {string} requirement - Plugin requirement description.
 * @returns {object} - Plugin configuration metadata.
 */
function generatePluginConfig(requirement) {
  if (!requirement || typeof requirement !== 'string') {
    requirement = 'Default plugin functionality';
  }

  const pluginName = toPluginIdentifier(requirement);
  const pluginDesc = toPluginDescription(requirement);
  const now = new Date().toISOString();

  return {
    name: pluginName,
    description: pluginDesc,
    version: '1.0.0',
    runtime: 'node',
    format: 'commonjs',
    entry: 'index.js',
    author: 'Auto-generated',
    createdAt: now,
    updatedAt: now,
    permissions: [],
    dependencies: {},
    input: {
      type: 'object',
      required: ['input'],
      properties: {
        input: {
          type: 'string',
          description: 'Primary input text for the plugin.',
          minLength: 1
        }
      }
    },
    output: {
      type: 'object',
      required: ['code', 'message', 'data'],
      properties: {
        code: { type: 'integer', description: 'Status code (0 = success).' },
        message: { type: 'string', description: 'Status message.' },
        data: { type: 'object', description: 'Response payload.' }
      }
    },
    timeout: 30000,
    memory: 256
  };
}

/**
 * Generates usage instructions for the plugin.
 *
 * @param {string} pluginName - Name of the generated plugin.
 * @param {string} requirement - Original requirement description.
 * @returns {string} - Markdown-formatted usage instructions.
 */
function generateUsageInstructions(pluginName, requirement) {
  return `## Usage Instructions for "${pluginName}"

//## 1. Install
Place the generated `index.js` and `package.json` into your plugin directory.

//## 2. Configure
Update `config.json` (or your platform's config) with the plugin metadata provided in the `config` field.

//## 3. Invoke
Call the plugin via the Coze platform by sending a JSON payload:

```json
{
  "plugin_requirement": "${requirement.replace(/"/g, '\\"')}"
}
```

//## 4. Response Format
The plugin returns:

```json
{
  "code": 0,
  "message": "Success",
  "data": { ... }
}
```

//## 5. Customization
Open `index.js` and replace the "TODO" section with your business logic.
`;
}

// -----------------------------------------------------------------------------
// Main Handler
// -----------------------------------------------------------------------------

/**
 * Main entry point for the Coze Plugin Code Generator.
 *
 * @param {object} params - Input parameters.
 *   @param {string} params.plugin_requirement - Required. Plugin functionality description.
 *   @param {string} [params.request] - Optional fallback requirement field.
 *   @param {string} [params.query] - Optional fallback query field.
 * @returns {object} - Response object.
 *   @returns {number} code - 0 for success, 400 for bad request, 500 for internal error.
 *   @returns {string} message - Human-readable status message.
 *   @returns {object} data - Generated plugin artifacts.
 */
function handler(params) {
  try {
    // Validate input schema
    const validation = validateSchema(params, INPUT_SCHEMA, 'params');
    if (!validation.valid) {
      return {
        code: 400,
        message: 'Input validation failed: ' + validation.errors.join('; '),
        data: null
      };
    }

    // Normalize and validate requirement content
    const requirement = normalizeRequirement(params);
    if (requirement.length === 0) {
      return {
        code: 400,
        message: 'Input validation failed: plugin_requirement (or fallback fields) must contain non-empty text.',
        data: null
      };
    }

    // Generate artifacts
    const pluginName = toPluginIdentifier(requirement);
    const pluginDescription = toPluginDescription(requirement);
    const code = generatePluginCode(requirement);
    const config = generatePluginConfig(requirement);
    const usageInstructions = generateUsageInstructions(pluginName, requirement);
    const generationTime = new Date().toISOString();

    // Build response data
    const data = {
      pluginName,
      pluginDescription,
      code,
      config,
      usageInstructions,
      generationTime
    };

    // Validate output schema (self-check)
    const outputValidation = validateSchema(
      { code: 0, message: 'Success', data },
      OUTPUT_SCHEMA,
      'response'
    );
    if (!outputValidation.valid) {
      return {
        code: 500,
        message: 'Output validation failed: ' + outputValidation.errors.join('; '),
        data: null
      };
    }

    return {
      code: 0,
      message: 'Plugin generated successfully.',
      data
    };
  } catch (error) {
    return {
      code: 500,
      message: 'Internal server error: ' + (error && error.message ? error.message : String(error)),
      data: null
    };
  }
}

// -----------------------------------------------------------------------------
// Exports
// -----------------------------------------------------------------------------

module.exports = {
  PLUGIN_METADATA,
  INPUT_SCHEMA,
  OUTPUT_SCHEMA,
  handler,
  generatePluginCode,
  generatePluginConfig,
  validateSchema,
  normalizeRequirement,
  toPluginIdentifier,
  toPluginDescription,
  generateUsageInstructions
};
