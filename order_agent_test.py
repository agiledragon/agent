"""
智能点餐助手 Agent 测试文件
使用 GWT (Given-When-Then) 格式
"""
import pytest
from order_agent import ask_menu_price, calculate, MENU


class TestAskMenuPrice:
    """测试查询菜品价格功能"""
    
    def test_query_existing_item_burger(self):
        """测试查询存在的菜品 - 汉堡"""
        # Given: 菜单中有汉堡，价格25元
        item = "汉堡"
        expected_price = 25
        
        # When: 查询汉堡价格
        result = ask_menu_price(item)
        
        # Then: 返回汉堡的价格信息
        assert result == f"{item}的价格是{expected_price}元"
    
    def test_query_existing_item_cola(self):
        """测试查询存在的菜品 - 可乐"""
        # Given: 菜单中有可乐，价格8元
        item = "可乐"
        expected_price = 8
        
        # When: 查询可乐价格
        result = ask_menu_price(item)
        
        # Then: 返回可乐的价格信息
        assert result == f"{item}的价格是{expected_price}元"
    
    def test_query_non_existing_item(self):
        """测试查询不存在的菜品"""
        # Given: 菜单中没有寿司
        item = "寿司"
        
        # When: 查询寿司价格
        result = ask_menu_price(item)
        
        # Then: 返回提示信息，告知菜品不存在
        assert "抱歉，菜单中没有寿司" in result
        assert "可选菜品有" in result
    
    def test_query_with_whitespace(self):
        """测试带空格的输入"""
        # Given: 输入带有前后空格
        item = "  汉堡  "
        
        # When: 查询价格
        result = ask_menu_price(item)
        
        # Then: 正确返回价格（自动去除空格）
        assert result == "汉堡的价格是25元"


class TestCalculate:
    """测试计算功能"""
    
    def test_simple_addition(self):
        """测试简单加法"""
        # Given: 一个加法表达式
        expression = "25 + 8"
        
        # When: 计算表达式
        result = calculate(expression)
        
        # Then: 返回正确结果
        assert result == "33元"
    
    def test_multiplication_and_addition(self):
        """测试乘法和加法组合"""
        # Given: 2份汉堡(25元) + 1杯可乐(8元)的计算表达式
        expression = "25*2 + 8*1"
        
        # When: 计算表达式
        result = calculate(expression)
        
        # Then: 返回正确总价
        assert result == "58元"
    
    def test_complex_expression(self):
        """测试复杂表达式"""
        # Given: 3份汉堡 + 2份薯条 + 2杯可乐
        expression = "25*3 + 12*2 + 8*2"
        
        # When: 计算表达式
        result = calculate(expression)
        
        # Then: 返回正确总价 (75 + 24 + 16 = 115)
        assert result == "115元"
    
    def test_invalid_expression(self):
        """测试无效表达式"""
        # Given: 一个无效的表达式
        expression = "abc + xyz"
        
        # When: 计算表达式
        result = calculate(expression)
        
        # Then: 返回错误信息
        assert "计算错误" in result


class TestMenuData:
    """测试菜单数据"""
    
    def test_menu_has_required_items(self):
        """测试菜单包含必要菜品"""
        # Given: 期望的菜品列表
        required_items = ["汉堡", "薯条", "可乐"]
        
        # When: 检查菜单
        # Then: 所有必要菜品都存在
        for item in required_items:
            assert item in MENU, f"菜单中应该包含{item}"
    
    def test_menu_prices_are_positive(self):
        """测试所有价格都是正数"""
        # Given: 菜单数据
        # When: 遍历所有价格
        # Then: 所有价格都大于0
        for item, price in MENU.items():
            assert price > 0, f"{item}的价格应该大于0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

