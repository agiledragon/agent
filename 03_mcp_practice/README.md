# 🔧 MCP Practice - 程序员助手工具集

## 📖 简介

本目录包含一个 MCP Server 和一个 Agent 示例，用于演示 MCP 协议的工作原理。

## 🚀 快速开始

```bash
# 安装依赖
pip install fastmcp mcp requests

# 设置环境变量
export TENCENT_API_KEY="你的API密钥"

# 运行 Agent
python3 dev_agent.py
```

## 📁 文件说明

| 文件            | 说明                        |
| --------------- | --------------------------- |
| `mcp_server.py` | MCP Server，提供 3 个工具   |
| `dev_agent.py`  | Agent 示例，调用 MCP Server |

---

## 🔧 工具使用说明

### 1️⃣ generate_uuid - 生成 UUID

```
生成 UUID

参数：
  - version: UUID 版本（可选，默认 4）
    可选值：1, 4

示例：
  "帮我生成一个 UUID"
  "生成 UUID v1"
```

### 2️⃣ generate_hash - 生成哈希值

```
生成文本的哈希值

参数：
  - text: 要哈希的文本（必填）
  - algorithm: 算法（可选，默认 md5）
    可选值：md5, sha1, sha256, sha512

示例：
  "计算 password123 的 MD5 值"
  "帮我生成 Hello World 的 SHA256 哈希"
```

### 3️⃣ base64_encode - Base64 编码

```
对文本进行 Base64 编码

参数：
  - text: 要编码的文本（必填）

示例：
  "把 Hello World 进行 base64 编码"
  "帮我 base64 编码: Hello MCP"
```

---

## 💬 使用示例

启动 Agent 后，可以这样交互：

```
👤 用户: 帮我生成一个 UUID

🔧 Action: generate_uuid(version=4)
📋 Observation: 🆔 UUID v4: a1b2c3d4-e5f6-7890-abcd-ef1234567890

Answer: 已为您生成 UUID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

```
👤 用户: 计算 password123 的 MD5 值

🔧 Action: generate_hash(text='password123', algorithm='md5')
📋 Observation: 
🔑 MD5 哈希值:
482c811da5d5b4bc6d497ffa98491e38

Answer: "password123" 的 MD5 值是: 482c811da5d5b4bc6d497ffa98491e38
```

```
👤 用户: base64 编码 Hello MCP

🔧 Action: base64_encode(text='Hello MCP')
📋 Observation: 🔐 Base64 编码结果: SGVsbG8gTUNQ

Answer: "Hello MCP" 的 Base64 编码是: SGVsbG8gTUNQ
```

---

## 🔗 在 Cursor 中配置

创建 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
     "dev-tools": {
      "command": "python3",
      "args": ["/绝对路径/mcp_server.py"]
    }
  }
}
```

---

## 📚 学习资源

- [MCP 协议文档](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://gofastmcp.com/)
