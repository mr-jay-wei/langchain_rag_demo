# 提示词管理系统

本目录包含了RAG系统中使用的所有提示词模板，实现了提示词与代码的解耦。

## 文件结构

```
prompts/
├── README.md                 # 本说明文件
├── qa_prompt.txt            # 问答提示词模板
└── query_rewrite_prompt.txt # 问题改写提示词模板
```

## 提示词文件说明

### qa_prompt.txt
用于指导LLM如何基于检索到的上下文回答用户问题。

**变量:**
- `{context}`: 检索到的相关文档内容
- `{question}`: 用户提出的问题

### query_rewrite_prompt.txt
用于指导LLM如何将用户的原始问题改写成多个相关问题，以提高检索覆盖面。

**变量:**
- `{original_query}`: 用户的原始问题
- `{count}`: 需要生成的改写问题数量

## 使用方法

### 在代码中使用提示词管理器

```python
from rag.prompt_manager import (
    get_qa_prompt_template,
    get_query_rewrite_prompt_template,
    load_qa_prompt,
    load_query_rewrite_prompt
)

# 获取提示词模板对象
qa_template = get_qa_prompt_template()
rewrite_template = get_query_rewrite_prompt_template()

# 格式化提示词
formatted_prompt = qa_template.format(
    context="相关文档内容",
    question="用户问题"
)

# 直接加载提示词内容
qa_prompt_content = load_qa_prompt()
```

### 修改提示词

1. 直接编辑对应的 `.txt` 文件
2. 保存文件后，系统会自动使用新的提示词内容
3. 如果需要立即生效，可以调用 `prompt_manager.reload_prompt(prompt_name)`

### 添加新的提示词

1. 在 `prompts/` 目录下创建新的 `.txt` 文件
2. 在 `prompt_manager.py` 中添加对应的辅助函数
3. 在需要使用的地方导入并使用

## 优势

1. **解耦性**: 提示词与代码分离，便于维护和修改
2. **可维护性**: 集中管理所有提示词，便于版本控制和协作
3. **性能优化**: 内置缓存机制，避免重复读取文件
4. **灵活性**: 支持动态重新加载，便于调试和优化
5. **一致性**: 统一的接口和使用方式

## 最佳实践

1. **命名规范**: 使用描述性的文件名，如 `qa_prompt.txt`、`summary_prompt.txt`
2. **变量标记**: 使用 `{variable_name}` 格式标记模板变量
3. **文档注释**: 在提示词文件开头添加注释说明用途和变量
4. **版本控制**: 将提示词文件纳入版本控制，跟踪变更历史
5. **测试验证**: 修改提示词后进行充分测试，确保效果符合预期

## 示例

### 创建新的提示词文件

```bash
# 创建摘要提示词文件
echo "请对以下内容进行简洁的摘要：

{content}

摘要：" > prompts/summary_prompt.txt
```

### 在代码中使用新提示词

```python
# 在 prompt_manager.py 中添加
def get_summary_prompt_template():
    return prompt_manager.get_template("summary_prompt")

# 在业务代码中使用
from rag.prompt_manager import get_summary_prompt_template

summary_template = get_summary_prompt_template()
formatted_prompt = summary_template.format(content="要摘要的内容")
```