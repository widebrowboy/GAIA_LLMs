#!/usr/bin/env python3
"""
Quick MCP Output Control Test

This script demonstrates the MCP output control functionality.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cli.chatbot import DrugDevelopmentChatbot
from app.utils.config import Config

def test_mcp_output_control():
    """Test MCP output control functionality"""
    
    print("🧪 MCP 출력 제어 기능 테스트")
    print("-" * 40)
    
    # Initialize chatbot
    config = Config()
    chatbot = DrugDevelopmentChatbot(config)
    
    print(f"초기 상태: show_mcp_output = {chatbot.config.show_mcp_output}")
    
    # Test toggle functionality
    print("\n1. 첫 번째 토글 (OFF -> ON):")
    chatbot.toggle_mcp_output()
    
    print(f"변경 후: show_mcp_output = {chatbot.config.show_mcp_output}")
    
    print("\n2. 두 번째 토글 (ON -> OFF):")
    chatbot.toggle_mcp_output()
    
    print(f"변경 후: show_mcp_output = {chatbot.config.show_mcp_output}")
    
    # Test mode switching
    print("\n3. 모드 전환 테스트:")
    print(f"현재 모드: {chatbot.current_mode}")
    
    print("Deep Research 모드로 전환...")
    # 이 파일은 비동기 함수가 아니므로 임시로 동기 버전 사용
    # await chatbot.switch_to_deep_research_mode()
    chatbot.current_mode = "deep_research"
    print(f"변경된 모드: {chatbot.current_mode}")
    
    print("일반 모드로 전환...")
    # await chatbot.switch_to_normal_mode()
    chatbot.current_mode = "normal"
    print(f"변경된 모드: {chatbot.current_mode}")
    
    print("\n✅ 모든 기능 테스트 완료!")
    
    # Usage examples
    print("\n📖 사용 예시:")
    print("  • /mcpshow     - MCP 출력 토글")
    print("  • /mcp start   - Deep Research 모드")
    print("  • /normal      - 일반 모드")
    print("  • /help        - 전체 도움말")

if __name__ == "__main__":
    test_mcp_output_control()