
def select_optimal_model(message_length, complexity="normal", response_type="text"):
    """
    메시지 특성에 따라 최적 모델 선택
    
    Args:
        message_length: 메시지 길이
        complexity: 복잡도 ("simple", "normal", "complex")
        response_type: 응답 타입 ("text", "analysis", "research")
    
    Returns:
        str: 최적 모델명
    """
    # 메모리 사용량 기준
    available_memory = get_available_memory()  # GB 단위
    
    # 1. 단순한 질문이나 짧은 응답
    if complexity == "simple" or message_length < 100:
        return "txgemma-chat:latest"
    
    # 2. 메모리 부족 시
    if available_memory < 20:
        return "txgemma-chat:latest"
    
    # 3. 복잡한 분석이나 연구 작업
    if complexity == "complex" or response_type == "research":
        if available_memory >= 25:
            return "Gemma3:27b-it-q4_K_M"
        else:
            return "txgemma-chat:latest"
    
    # 4. 기본값
    return "txgemma-chat:latest"

def get_available_memory():
    """사용 가능한 메모리 확인 (GB)"""
    import psutil
    memory = psutil.virtual_memory()
    return memory.available / (1024**3)
