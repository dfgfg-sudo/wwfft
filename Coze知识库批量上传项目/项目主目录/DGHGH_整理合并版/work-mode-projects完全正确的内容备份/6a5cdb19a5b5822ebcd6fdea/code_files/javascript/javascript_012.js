// 自动化测试配置示例
// package.json 片段
{
  "scripts": {
    "test": "jest --coverage",
    "test:unit": "jest --testPathPattern='.*unit\\.test\\.js$'",
    "test:integration": "jest --testPathPattern='.*integration\\.test\\.js$'",
    "test:e2e": "cypress run",
    "lint": "eslint src/",
    "lint:fix": "eslint src/ --fix"
  },
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{js,jsx}",
      "!src/**/*.test.{js,jsx}",
      "!src/index.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}

// 测试覆盖率检查脚本
// check-coverage.sh
#!/bin/bash
MIN_COVERAGE=80
COVERAGE_FILE="coverage/coverage-summary.json"

if [ -f "$COVERAGE_FILE" ]; then
    COVERAGE=$(node -p "require('$COVERAGE_FILE').total.lines.pct")
    echo "当前覆盖率: $COVERAGE%"
    
    if (( $(echo "$COVERAGE < $MIN_COVERAGE" | bc -l) )); then
        echo "❌ 覆盖率低于 $MIN_COVERAGE%"
        exit 1
    else
        echo "✅ 覆盖率达标"
    fi
else
    echo "覆盖率文件不存在"
    exit 1
fi