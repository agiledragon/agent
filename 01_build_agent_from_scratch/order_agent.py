"""
智能点餐助手 Agent
底层实现：听需求 → 查菜单 → 算价格 → 给结果
对接大模型：deepseek-v3 (腾讯云API)
"""
import os
import re
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
        # 安全地计算数学表达式
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

    def invoke(self, message: str) -> str:
        """发送消息并获取回复"""
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self) -> str:
        """调用大模型API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        data = {
            "model": MODEL,
            "messages": self.messages,
            "temperature": 0,
            "stream": False
        }
        
        response = requests.post(API_URL, headers=headers, json=data, verify=False)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


PROMPT = """
你是一个智能点餐助手，负责帮助顾客完成点餐并计算总价。

## 重要规则
1. 每次回复只输出一行 Thought（包含一个工具调用），然后停止
2. 等待系统返回 Observation 后，再输出下一行 Thought
3. 完成后输出 Thought + Answer

## 可用工具
1. ask_menu_price: 查询单个菜品价格，如 [Call: ask_menu_price: 咖啡]
2. calculate: 计算总价，如 [Call: calculate: 10*1 + 8*2]

## 输出格式
Thought: 思考内容[Call: 工具名: 参数]

## 会话示例

用户: 我要一杯咖啡

你输出: Thought: 查询咖啡价格[Call: ask_menu_price: 咖啡]
系统返回: Action: ask_menu_price(咖啡)
系统返回: Observation: 咖啡的价格是15元

你输出: Thought: 得到价格15元，输出答案
你输出: Answer: 您的订单：咖啡x1=15元，总计15元
"""


# ==================== 主查询函数 ====================
# 从 Thought 中匹配工具调用意图 [Call: tool_name: params]
CALL_RE = re.compile(r'\[Call: (\w+): ([^\]]+)\]', re.MULTILINE)

# 已注册的工具
KNOWN_ACTIONS = {
    "ask_menu_price": ask_menu_price,
    "calculate": calculate
}


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
        
        # Thought: 大模型思考并输出工具调用意图
        result = agent.invoke(next_prompt)
        print(f"\n{result}")
        
        # 从 Thought 中匹配工具调用意图
        calls = CALL_RE.findall(result)
        
        if calls:
            tool_name, tool_input = calls[0]
            
            if tool_name not in KNOWN_ACTIONS:
                raise Exception(f"未知工具: {tool_name}: {tool_input}")
            
            # Action: 程序执行工具调用
            print(f"Action: {tool_name}({tool_input})")
            observation = KNOWN_ACTIONS[tool_name](tool_input)
            
            # Observation: 工具返回结果
            print(f"Observation: {observation}")
            
            next_prompt = f"Observation: {observation}"
        else:
            # 没有工具调用，说明已经完成
            print(f"\n✅ 点餐完成!")
            return result
    
    return "抱歉，处理超时，请重试。"


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("🍔 欢迎使用智能点餐助手!")
    print("=" * 50)
    print("菜单:")
    for item, price in MENU.items():
        print(f"  {item}: {price}元")
    print("=" * 50)
    
    # 示例点餐
    order = "我要2份汉堡和1杯可乐"
    print(f"\n👤 用户: {order}")
    
    result = query(order)

