// 文件位置：backend/domain/workflow/internal/nodes/custom/executor.go
// 本文件合并了原 custom.go 中的所有代码，无遗漏
package custom

import (
    "context"
)

// YourNode is the definition of your custom node.
type YourNode struct {
    // define any fields here which are needed during node execution
}

// Invoke is the execution method of your custom node.
// 实现 InvokableNode 接口
func (c *YourNode) Invoke(ctx context.Context, input map[string]any) (
    output map[string]any, err error) {
    // your business logic
    // 例如：从 input 中获取前驱节点数据，处理后返回 output
    return map[string]any{"result": "success"}, nil
}