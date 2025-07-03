import unittest
from app.cli.chatbot import DrugDevelopmentChatbot
from app.utils.config import Config

class TestDrugDevelopmentChatbot(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.chatbot = DrugDevelopmentChatbot(self.config)

    def test_initialization(self):
        """챗봇 초기화 테스트"""
        self.assertIsNotNone(self.chatbot)
        self.assertEqual(self.chatbot.config, self.config)

    def test_basic_response(self):
        """기본 응답 테스트"""
        response = self.chatbot.get_response("안녕하세요")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_health_supplement_query(self):
        """건강기능식품 관련 질문 테스트"""
        test_queries = [
            "비타민D의 효능은 무엇인가요?",
            "오메가3의 부작용이 있나요?",
            "프로바이오틱스의 효과적인 섭취 방법은?",
            "루테인의 권장 섭취량은 얼마인가요?"
        ]
        
        for query in test_queries:
            response = self.chatbot.get_response(query)
            self.assertIsNotNone(response)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            # 응답에 필수 키워드가 포함되어 있는지 확인
            self.assertTrue(any(keyword in response.lower() for keyword in 
                ["효능", "효과", "섭취", "권장", "부작용", "주의사항"]))

    def test_error_handling(self):
        """에러 처리 테스트"""
        # 빈 입력 테스트
        response = self.chatbot.get_response("")
        self.assertIsNotNone(response)
        self.assertTrue("질문을 입력해주세요" in response)

        # 매우 긴 입력 테스트
        long_input = "a" * 1000
        response = self.chatbot.get_response(long_input)
        self.assertIsNotNone(response)
        self.assertTrue("질문이 너무 깁니다" in response)

    def test_context_handling(self):
        """대화 맥락 처리 테스트"""
        # 연속된 대화 테스트
        self.chatbot.get_response("비타민C에 대해 알려주세요")
        response = self.chatbot.get_response("그럼 비타민D는요?")
        self.assertIsNotNone(response)
        self.assertTrue("비타민D" in response)

if __name__ == '__main__':
    unittest.main() 