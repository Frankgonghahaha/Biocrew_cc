# CrewAI模型支持说明

## 支持的模型

CrewAI支持多种大语言模型，不仅限于OpenAI的模型，还包括：

1. **阿里云Qwen系列模型**
2. **Anthropic Claude系列**
3. **Google Gemini系列**
4. **Hugging Face模型**
5. **本地部署模型**
6. **以及其他兼容OpenAI API的模型**

## 阿里云Qwen模型配置

要使用阿里云Qwen模型，需要进行以下配置：

### 1. 环境变量配置

在`.env`文件中设置以下变量：

```env
# Qwen模型配置
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your-actual-api-key-here
QWEN_MODEL_NAME=qwen-plus  # 或其他Qwen模型名称

# 兼容OpenAI的配置（CrewAI需要）
OPENAI_API_KEY=your-actual-api-key-here
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 2. 代码中使用方式

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_base=os.getenv('QWEN_API_BASE'),
    openai_api_key=os.getenv('QWEN_API_KEY'),
    model_name="qwen-plus"  # 或其他Qwen模型
)
```

## 常见问题及解决方案

### 1. AuthenticationError错误

**问题**：
```
litellm.AuthenticationError: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
```

**解决方案**：
确保同时设置了`QWEN_API_KEY`和`OPENAI_API_KEY`环境变量，且值相同。

### 2. BadRequestError错误

**问题**：
```
litellm.BadRequestError: LLM Provider NOT provided
```

**解决方案**：
确保模型名称格式正确，不需要添加提供者前缀（如`openai/`）。

## 可用的Qwen模型

阿里云提供了多种Qwen模型，可根据需求选择：

1. `qwen-turbo` - 推理能力较强，响应速度快
2. `qwen-plus` - 平衡推理效果和成本
3. `qwen-max` - 推理效果最佳，适合复杂任务
4. `qwen3-30b-a3b-instruct-2507` - 您当前使用的模型

## 配置验证

配置完成后，可以通过以下方式验证：

1. 检查环境变量是否正确设置
2. 运行`python3 check_config.py`检查配置
3. 运行`python3 test_system.py`测试系统功能

## 注意事项

1. 确保API密钥正确且有足够权限
2. 确保网络可以访问API端点
3. 根据实际使用的模型调整模型名称
4. 部分模型可能需要额外的参数配置