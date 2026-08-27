# Coze IDE 元数据参数填写指南

## 输入参数（Input）-- 共 5 个

在 Coze IDE 右侧「元数据」->「输入参数」中逐个添加：

### 参数 1：zip_base64
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `zip_base64` |
| 参数类型 | `string` |
| 是否必填 | `true`（是） |
| 参数描述 | `ZIP文件的Base64编码字符串。将文件夹压缩为ZIP后，转为Base64编码传入。` |

### 参数 2：path_prefix
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `path_prefix` |
| 参数类型 | `string` |
| 是否必填 | `false`（否） |
| 参数描述 | `知识库路径前缀，如"知识库"。会在每个文件路径前加上此前缀，默认为空。` |

### 参数 3：allowed_extensions
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `allowed_extensions` |
| 参数类型 | `array` |
| 是否必填 | `false`（否） |
| 参数描述 | `允许的文件扩展名白名单，如[".md",".txt",".pdf"]。为空则默认支持全部40+种格式。` |

> **array 类型填写说明**：
> - 在 Coze IDE 中，array 类型的子元素类型通常选择 `string`
> - 默认值可以留空，或填写 `[".md", ".txt", ".json"]` 等

### 参数 4：max_file_size_mb
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `max_file_size_mb` |
| 参数类型 | `number` |
| 是否必填 | `false`（否） |
| 参数描述 | `单个文件最大大小（MB），超过此大小的文件会被跳过。默认20MB。` |

### 参数 5：skip_hidden
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `skip_hidden` |
| 参数类型 | `boolean` |
| 是否必填 | `false`（否） |
| 参数描述 | `是否跳过隐藏文件（以.开头的文件）。默认true，建议保持开启以保证安全。` |

---

## 输出参数（Output）-- 共 11 个

在 Coze IDE 右侧「元数据」->「输出参数」中逐个添加。

**更简单的方法**：先运行一次测试（用提供的Base64数据），然后点击「更新输出参数」按钮，IDE会自动从实际输出中提取参数结构。如果自动提取不完整，再手动补充以下参数。

### 参数 1：success
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `success` |
| 参数类型 | `boolean` |
| 参数描述 | `是否全部处理成功。true表示所有文件都正常处理，false表示有失败或错误。` |

### 参数 2：total_count
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `total_count` |
| 参数类型 | `integer` |
| 参数描述 | `ZIP压缩包内的总文件数量（未过滤前）。` |

### 参数 3：success_count
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `success_count` |
| 参数类型 | `integer` |
| 参数描述 | `成功处理的文件数量。` |

### 参数 4：fail_count
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `fail_count` |
| 参数类型 | `integer` |
| 参数描述 | `处理失败的文件数量。` |

### 参数 5：skipped_count
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `skipped_count` |
| 参数类型 | `integer` |
| 参数描述 | `被跳过的文件数量（隐藏文件、不支持的格式、超过大小限制等）。` |

### 参数 6：processing_time_ms
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `processing_time_ms` |
| 参数类型 | `integer` |
| 参数描述 | `处理耗时，单位毫秒。` |

### 参数 7：directory_tree
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `directory_tree` |
| 参数类型 | `string` |
| 参数描述 | `ZIP压缩包的目录树结构，以文本形式展示文件夹层级关系。` |

### 参数 8：documents
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `documents` |
| 参数类型 | `array` |
| 参数描述 | `知识库文档列表。每个元素是一个文档对象，包含id、title、path、content、format等字段。` |

> **array 类型子结构说明**：
> `documents` 是一个数组，每个元素的类型是 `object`（对象）。对象包含以下字段：
> - `id`: string -- 文档唯一标识
> - `title`: string -- 文档标题
> - `source_path`: string -- 原始文件在ZIP中的路径
> - `path`: string -- 知识库中的显示路径（含前缀）
> - `content`: string -- 提取的纯文本内容
> - `format`: string -- 文件格式（markdown/html/json/csv/code/config等）
> - `file_size`: integer -- 文件大小（字节）
> - `word_count`: integer -- 字数统计
> - `success`: boolean -- 是否处理成功
> - `error_message`: string -- 错误信息（失败时才有）
> - `processed_at`: string -- 处理时间戳（ISO格式）

### 参数 9：summary
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `summary` |
| 参数类型 | `string` |
| 参数描述 | `处理摘要信息，包含成功数、失败数、跳过数、总计数等统计。` |

### 参数 10：logs
| 字段 | 填写值 |
|------|--------|
| 参数名称 | `logs` |
| 参数类型 | `array` |
| 参数描述 | `处理日志数组，记录每一步操作的详细信息，便于调试和排查问题。` |

> **array 类型子结构说明**：
> `logs` 是一个字符串数组，每个元素类型是 `string`。

---

## array / array<> 类型填写方法详解

### 问题：Coze IDE 中 array 类型怎么填子类型？

**解答**：

1. 添加参数时，类型选择 `array`
2. 选择后，IDE 通常会显示一个「子元素类型」或「元素类型」的下拉框
3. 根据参数不同，选择对应的子类型：

| 参数名 | array 子类型 | 说明 |
|--------|-------------|------|
| allowed_extensions | `string` | 字符串数组，如 [".md", ".txt"] |
| documents | `object` | 对象数组，每个元素是一个文档对象 |
| logs | `string` | 字符串数组，每条日志是一个字符串 |

### 如果 IDE 没有显示子类型选项怎么办？

有些版本的 Coze IDE 可能用 `array<类型>` 的写法：
- `array<string>` -- 字符串数组
- `array<object>` -- 对象数组

在参数类型下拉框中直接选择带尖括号的类型即可。

---

## 快速配置检查清单

配置完成后，对照以下清单检查：

### 输入参数（5个）
- [ ] zip_base64 -- string -- 必填
- [ ] path_prefix -- string -- 选填
- [ ] allowed_extensions -- array<string> -- 选填
- [ ] max_file_size_mb -- number -- 选填
- [ ] skip_hidden -- boolean -- 选填

### 输出参数（10个）
- [ ] success -- boolean
- [ ] total_count -- integer
- [ ] success_count -- integer
- [ ] fail_count -- integer
- [ ] skipped_count -- integer
- [ ] processing_time_ms -- integer
- [ ] directory_tree -- string
- [ ] documents -- array<object>
- [ ] summary -- string
- [ ] logs -- array<string>

---

## 测试参数 JSON（Run测试时直接粘贴）

```json
{
  "zip_base64": "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",
  "path_prefix": "知识库",
  "skip_hidden": true
}
```
