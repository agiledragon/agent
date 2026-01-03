"""
智能点餐助手 Agent - Function Calling 版本
对接大模型：deepseek-v3 (腾讯云API)
"""
import os
import json
import requests

# ==================== 配置 ====================
API_URL = "https://api.lkeap.cloud.tencent.com/v1/chat/completions"
API_KEY = os.environ.get("TENCENT_API_KEY", "")
MODEL = "deepseek-v3"

# ==================== 菜单数据 ====================
MENU = {
    "汉堡": 25,
    "薯条": 12,
    "可乐": 8,
    "鸡翅": 18,
    "冰淇淋": 6,
    "咖啡": 15,
    "沙拉": 20,
    "披萨": 45,
    "三明治": 22,
    "奶茶": 10,
}

# ==================== 工具定义（JSON Schema）====================
tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_menu_price",
            "description": "查询菜品价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "菜品名称，如：汉堡、可乐、薯条"
                    }
                },
                "required": ["item_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如：25*2 + 8*1"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


# ==================== 工具实现 ====================
def ask_menu_price(item_name: str) -> str:
    """查询菜品价格"""
    item_name = item_name.strip()
    if item_name in MENU:
        return f"{item_name}的价格是{MENU[item_name]}元"
    else:
        available = "、".join(MENU.keys())
        return f"抱歉，菜单中没有{item_name}。可选菜品有：{available}"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{result}元"
    except Exception as e:
        return f"计算错误: {str(e)}"


# ==================== Agent 核心类 ====================
class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def invoke(self, message: str = "") -> dict:
        """发送消息并获取回复"""
        if message:  # FC 版本：空消息不添加（工具结果已通过 add_tool_result 添加）
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
        data = {
            "model": MODEL,
            "messages": self.messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0,
            "stream": False
        }
        
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
你是一个智能点餐助手，负责帮助顾客完成点餐并计算总价。

## 重要规则
1. 计算总价必须使用 calculate 工具
2. **calculate 返回结果后，不要再调用任何工具**，直接输出 Answer 结束对话

## 输出示例
Answer: 您的订单：咖啡x1=15元，总计15元

"""



# 已注册的工具
KNOWN_ACTIONS = {
    "ask_menu_price": ask_menu_price,
    "calculate": calculate,
}


# ==================== 主查询函数 ====================
def query(question: str, max_turns: int = 10) -> str:
    """
    执行点餐查询
    
    Args:
        question: 用户的点餐需求
        max_turns: 最大循环次数
    
    Returns:
        最终的订单信息
    """
    agent = Agent(PROMPT)
    next_prompt = question
    
    for i in range(max_turns):
        print(f"\n{'='*50}")
        print(f"第 {i+1} 轮对话")
        print(f"{'='*50}")
        
        # Thought: 大模型思考（使用 Function Calling）
        msg = agent.invoke(next_prompt)
        content = msg.get("content", "").strip()
        
        # 检查是否有工具调用
        if "tool_calls" in msg and msg["tool_calls"]:
            # 打印模型的思考过程（如果有）
            if content:
                print(f"\n{content}")
            
            for tool_call in msg["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                
                # 格式化参数显示
                if func_name == "ask_menu_price":
                    args_display = func_args["item_name"]
                elif func_name == "calculate":
                    args_display = func_args["expression"]
                else:
                    args_display = json.dumps(func_args, ensure_ascii=False)
                
                # Action: 程序执行工具调用
                print(f"Action: {func_name}({args_display})")
                
                # 执行工具
                if func_name in KNOWN_ACTIONS:
                    if func_name == "ask_menu_price":
                        result = KNOWN_ACTIONS[func_name](func_args["item_name"])
                    elif func_name == "calculate":
                        result = KNOWN_ACTIONS[func_name](func_args["expression"])
                    else:
                        result = "未知工具"
                else:
                    result = f"未知工具: {func_name}"
                
                # Observation: 工具返回结果
                print(f"Observation: {result}")
                
                # 将工具结果加入历史
                agent.add_tool_result(tool_call["id"], result)
            
            next_prompt = ""  # FC 版本不需要手动传递 Observation
        else:
            # 没有工具调用，输出最终回答
            import re
            content = re.sub(r'(Thought:.*?)\n\n+(Answer:)', r'\1\n\2', content, flags=re.DOTALL)
            print(f"\n{content}")
            print(f"\n✅ 点餐完成!")
            return content
    
    return "抱歉，处理超时，请重试。"


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("🍔 智能点餐助手（Function Calling 版）")
    print("=" * 50)
    print("菜单:")
    for item, price in MENU.items():
        print(f"  {item}: {price}元")
    print("=" * 50)
    
    # 示例点餐
    order = "我要2份汉堡和1杯可乐"
    print(f"\n👤 用户: {order}")
    
    result = query(order)
