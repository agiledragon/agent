# -*- coding: utf-8 -*-
"""
程序员助手 MCP Server
使用 FastMCP 提供实用的开发者工具（精简版：3 个核心工具）
"""
import hashlib
import base64
import uuid
from fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP(name="DevToolsServer")


# ==================== 工具 1：生成 UUID ====================
@mcp.tool()
def generate_uuid(version: int = 4) -> str:
    """
    生成 UUID
    
    Args:
        version: UUID 版本 (1 或 4)，默认 4
    """
    try:
        if version == 1:
            result = uuid.uuid1()
        else:
            result = uuid.uuid4()
        return f"🆔 UUID v{version}: {result}"
    except Exception as e:
        return f"❌ 生成失败: {str(e)}"


# ==================== 工具 2：生成哈希 ====================
@mcp.tool()
def generate_hash(text: str, algorithm: str = "md5") -> str:
    """
    生成哈希值
    
    Args:
        text: 要哈希的文本
        algorithm: 算法 (md5, sha1, sha256, sha512)，默认 md5
    """
    try:
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        if algorithm not in algorithms:
            return f"❌ 不支持的算法: {algorithm}，可选: {', '.join(algorithms.keys())}"
        
        hash_obj = algorithms[algorithm](text.encode('utf-8'))
        return f"🔑 {algorithm.upper()} 哈希值:\n{hash_obj.hexdigest()}"
    except Exception as e:
        return f"❌ 哈希失败: {str(e)}"


# ==================== 工具 3：Base64 编码 ====================
@mcp.tool()
def base64_encode(text: str) -> str:
    """
    Base64 编码
    
    Args:
        text: 要编码的文本
    """
    try:
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return f"🔐 Base64 编码结果:\n{encoded}"
    except Exception as e:
        return f"❌ 编码失败: {str(e)}"


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    print("🚀 启动程序员助手 MCP Server...")
    print(f"📦 服务名称: {mcp.name}")
    print("🔧 可用工具:")
    print("   - generate_uuid: 生成 UUID")
    print("   - generate_hash: 生成哈希值")
    print("   - base64_encode: Base64 编码")
    print("="*50)
    mcp.run()
