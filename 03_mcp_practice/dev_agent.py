# -*- coding: utf-8 -*-
"""
程序员助手 Agent - MCP 版本
对接大模型：deepseek-v3 (腾讯云API)
通过 MCP 协议调用工具服务
"""
import os
import json
import asyncio
import requests
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ==================== 配置 ====================
API_URL = "https://api.lkeap.cloud.tencent.com/v1/chat/completions"
API_KEY = os.environ.get("TENCENT_API_KEY", "")
MODEL = "deepseek-v3"

# MCP Server 配置
MCP_SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")


# ==================== MCP 客户端管理器 ====================
class MCPClient:
    """MCP 客户端，用于连接和调用 MCP Server"""
    
    def __init__(self):
        self.session: ClientSession = None
        self.tools = []
        self._tools_schema = []
    
    async def connect(self, server_script: str):
        """连接到 MCP Server"""
        import sys
        server_params = StdioServerParameters(
            command=sys.executable,  # 使用当前运行的 Python 解释器
            args=[server_script],
            env=None
        )
        
        # 创建 stdio 传输
        self._stdio_transport = stdio_client(server_params)
        self._read, self._write = await self._stdio_transport.__aenter__()
        
        # 创建并初始化会话
        self.session = ClientSession(self._read, self._write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        # 获取可用工具
        response = await self.session.list_tools()
        self.tools = response.tools
        self._build_tools_schema()
        
        print(f"✅ 已连接到 MCP Server，发现 {len(self.tools)} 个工具")
        return self
    
    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self._stdio_transport:
            await self._stdio_transport.__aexit__(None, None, None)
    
    def _build_tools_schema(self):
        """构建 OpenAI 兼容的工具 Schema"""
        self._tools_schema = []
        for tool in self.tools:
            schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema if tool.inputSchema else {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            self._tools_schema.append(schema)
    
    def get_tools_schema(self) -> list:
        """获取工具 Schema（用于 Function Calling）"""
        return self._tools_schema
    
    async def call_tool(self, name: str, arguments: dict) -> str:
        """调用 MCP 工具"""
        try:
            result = await self.session.call_tool(name, arguments)
            # 提取文本内容
            if result.content:
                texts = [c.text for c in result.content if hasattr(c, 'text')]
                return "\n".join(texts) if texts else str(result.content)
            return "工具执行完成（无输出）"
        except Exception as e:
            return f"❌ 工具调用失败: {str(e)}"


# ==================== Agent 核心类 ====================
class Agent:
    def __init__(self, system: str = "", mcp_client: MCPClient = None):
        self.system = system
        self.messages = []
        self.mcp_client = mcp_client
        if self.system:
            self.messages.append({"role": "system", "content": system})
    
    def invoke(self, message: str = "") -> dict:
        """发送消息并获取回复"""
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append(result)
        return result
    
    def execute(self) -> dict:
        """调用大模型 API（使用 Function Calling）"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        # 从 MCP Client 获取工具定义
        tools = self.mcp_client.get_tools_schema() if self.mcp_client else []
        
        data = {
            "model": MODEL,
            "messages": self.messages,
            "temperature": 0,
            "stream": False
        }
        
        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"
        
        response = requests.post(API_URL, headers=headers, json=data, verify=False)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]
    
    def add_tool_result(self, tool_call_id: str, result: str):
        """添加工具执行结果到消息历史"""
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        })


PROMPT = """
你是一个智能程序员助手，可以帮助开发者完成各种编程任务。

## 你可以使用的工具
- generate_uuid: 生成 UUID
- generate_hash: 生成哈希值 (MD5, SHA256 等)
- base64_encode: Base64 编码

## 重要规则
1. 根据用户需求选择合适的工具
2. 完成任务后，给出清晰的总结

## 输出格式
完成任务后，以 "Answer:" 开头给出最终回答
"""


# ==================== 主查询函数 ====================
async def query(question: str, mcp_client: MCPClient, max_turns: int = 10) -> str:
    """
    执行查询
    
    Args:
        question: 用户的需求
        mcp_client: MCP 客户端
        max_turns: 最大循环次数
    
    Returns:
        最终的回答
    """
    agent = Agent(PROMPT, mcp_client)
    next_prompt = question
    
    for i in range(max_turns):
        print(f"\n{'='*60}")
        print(f"第 {i+1} 轮对话")
        print(f"{'='*60}")
        
        # 大模型思考（使用 Function Calling）
        msg = agent.invoke(next_prompt)
        content = msg.get("content", "").strip()
        
        # 检查是否有工具调用
        if "tool_calls" in msg and msg["tool_calls"]:
            if content:
                print(f"\n💭 思考: {content}")
            
            for tool_call in msg["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                
                # 显示工具调用
                args_str = ", ".join(f"{k}={repr(v)}" for k, v in func_args.items())
                print(f"\n🔧 Action: {func_name}({args_str})")
                
                # 通过 MCP 调用工具
                result = await mcp_client.call_tool(func_name, func_args)
                
                # 显示结果
                print(f"\n📋 Observation:\n{result}")
                
                # 将工具结果加入历史
                agent.add_tool_result(tool_call["id"], result)
            
            next_prompt = ""
        else:
            # 没有工具调用，输出最终回答
            print(f"\n{content}")
            print(f"\n✅ 任务完成!")
            return content
    
    return "抱歉，处理超时，请重试。"


# ==================== 交互式会话 ====================
async def interactive_session():
    """交互式会话"""
    print("🤖 程序员助手（MCP 版）")
    print("="*60)
    print("输入你的需求，输入 'quit' 或 'exit' 退出")
    print("="*60)
    
    # 连接 MCP Server
    mcp_client = MCPClient()
    await mcp_client.connect(MCP_SERVER_SCRIPT)
    
    print("\n📦 可用工具列表:")
    for tool in mcp_client.tools:
        # 只取 description 的第一行（简短描述）
        desc = (tool.description or "").split('\n')[0].strip()
        print(f"   • {tool.name}: {desc}")
    print()
    
    try:
        while True:
            try:
                user_input = input("\n👤 用户: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                await query(user_input, mcp_client)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
    finally:
        await mcp_client.disconnect()


# ==================== 单次查询演示 ====================
async def demo():
    """演示模式"""
    print("🤖 程序员助手（MCP 版）- 演示模式")
    print("="*60)
    
    # 连接 MCP Server
    mcp_client = MCPClient()
    await mcp_client.connect(MCP_SERVER_SCRIPT)
    
    print("\n📦 可用工具列表:")
    for tool in mcp_client.tools:
        # 只取 description 的第一行（简短描述）
        desc = (tool.description or "").split('\n')[0].strip()
        print(f"   • {tool.name}: {desc}")
    
    try:
        # 演示查询
        demos = [
            "帮我生成一个 UUID",
            "把时间戳 1704067200 转换成日期时间",
            "帮我 base64 编码这段文本: Hello, MCP!",
        ]
        
        for demo_query in demos[:1]:  # 只演示一个
            print(f"\n{'='*60}")
            print(f"👤 用户: {demo_query}")
            await query(demo_query, mcp_client)
    finally:
        await mcp_client.disconnect()


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    import sys
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo())
    else:
        asyncio.run(interactive_session())

