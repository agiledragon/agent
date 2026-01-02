# 🤖 Agent 从零到一

> 100 行代码实现一个 Agent，从原理到实践

## 📖 项目简介

本项目是 AI Agent 的学习与实践仓库，通过**动手造轮子**的方式深入理解 Agent 的核心原理。从最简单的 ReAct 模式开始，逐步探索 Function Calling、MCP、A2A 协议、主流框架到多 Agent 协作系统。

## 🎯 学习路线

| 阶段  | 主题                 |   状态   | 说明                       |
| :---: | -------------------- | :------: | -------------------------- |
|   1   | **从零实现 Agent**   |  ✅ 完成  | 100 行代码实现 ReAct 模式  |
|   2   | **Function Calling** | 🚧 进行中 | OpenAI/Claude 原生工具调用 |
|   3   | **MCP 协议**         | ⏳ 待开始 | Model Context Protocol     |
|   4   | **A2A 协议**         | ⏳ 待开始 | Agent-to-Agent 通信        |
|   5   | **Agent 框架**       | ⏳ 待开始 | LangChain / LangGraph      |
|   6   | **多 Agent 协作**    | ⏳ 待开始 | 多智能体协作系统           |

---

## 📚 第一阶段：从零实现 Agent

### 核心概念

```
┌─────────────────────────────────────────────────────────────┐
│                        ReAct 循环                           │
│                                                             │
│   用户输入 ──▶ Thought(思考) ──▶ Action(行动) ──▶ Observation(观察)
│                    │                                 │      │
│                    │◀────────────────────────────────┘      │
│                    │                                        │
│                    └──────▶ Answer(输出) ──▶ 用户           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 实现架构

```
order_agent.py (200行)
├── Agent 类           # 核心：消息管理 + LLM 调用
├── Tools             # 工具函数：ask_menu_price, calculate
├── Prompt            # ReAct 提示词模板
└── query()           # 主循环：解析 → 执行 → 观察
```

### 代码结构

```python
# 1. Agent 核心类 - 管理对话历史，调用大模型
class Agent:
    def __init__(self, system=""): ...
    def invoke(self, message): ...    # 发送消息
    def execute(self): ...            # 调用 LLM API

# 2. 工具函数 - Agent 可以调用的能力
def ask_menu_price(item): ...         # 查询价格
def calculate(expression): ...        # 计算表达式

# 3. 主循环 - ReAct 模式核心
def query(question, max_turns=10):
    agent = Agent(PROMPT)
    while i < max_turns:
        result = agent.invoke(prompt)      # Thought
        if has_tool_call(result):
            observation = execute_tool()    # Action → Observation
            next_prompt = f"Observation: {observation}"
        else:
            return result                   # Answer
```

### 运行示例

```bash
# 设置 API Key
export TENCENT_API_KEY="your-api-key"

# 运行点餐助手
python order_agent.py
```

**对话效果：**
```
👤 用户: 我要2份汉堡和1杯可乐

Thought: 用户想要点2份汉堡和1杯可乐，我需要先查询汉堡的单价[Call: ask_menu_price: 汉堡]
Action: ask_menu_price(汉堡)
Observation: 汉堡的价格是25元

Thought: 已知汉堡25元，还需要查询可乐价格[Call: ask_menu_price: 可乐]
Action: ask_menu_price(可乐)
Observation: 可乐的价格是8元

Thought: 汉堡25元，可乐8元，现在计算总价[Call: calculate: 25*2 + 8*1]
Action: calculate(25*2 + 8*1)
Observation: 58元

Answer: 您的订单：汉堡x2=50元，可乐x1=8元，总计58元。感谢您的点餐！
```

---

## 📚 第二阶段：Function Calling（计划中）

> 从手动解析升级为 LLM 原生工具调用

### 对比

| 方式             | 工具调用                      | 优点         | 缺点         |
| ---------------- | ----------------------------- | ------------ | ------------ |
| ReAct            | 正则解析 `[Call: tool: args]` | 简单直观     | 解析不稳定   |
| Function Calling | LLM 原生 JSON                 | 结构化、可靠 | 依赖模型支持 |

### 计划内容
- [ ] OpenAI Function Calling
- [ ] Claude Tool Use
- [ ] 对比两种实现方式

---

## 📚 第三阶段：MCP 协议（计划中）

> Model Context Protocol - Anthropic 提出的工具标准化协议

### 计划内容
- [ ] 理解 MCP 协议设计
- [ ] 实现 MCP Server
- [ ] 接入 MCP Client

---

## 📚 第四阶段：A2A 协议（计划中）

> Agent-to-Agent - Google 提出的 Agent 间通信协议

### 计划内容
- [ ] 理解 A2A 协议
- [ ] Agent Card 设计
- [ ] 多 Agent 通信实践

---

## 📚 第五阶段：Agent 框架（计划中）

> 站在巨人的肩膀上

### 计划内容
- [ ] LangChain Agent
- [ ] LangGraph 工作流
- [ ] 框架 vs 手写对比

---

## 📚 第六阶段：多 Agent 协作（计划中）

> 多智能体协作系统

### 计划内容
- [ ] Agent 角色设计
- [ ] 协作模式（顺序/并行/讨论）
- [ ] 实战项目

---

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/your-username/agent.git
cd agent

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export TENCENT_API_KEY="your-api-key"

# 运行 Agent
python order_agent.py

# 运行测试
pytest order_agent_test.py -v
```

## 📁 项目结构

```
agent/
├── order_agent.py          # 第一阶段：ReAct Agent 实现
├── order_agent_test.py     # 测试文件
├── requirements.txt        # 依赖
├── README.md
└── LICENSE
```

## 🔗 参考资源

### 论文
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

### 协议与规范
- [MCP - Model Context Protocol](https://modelcontextprotocol.io/)
- [A2A - Agent-to-Agent Protocol](https://github.com/google/A2A)

### 框架
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)

## 📄 License

MIT License

