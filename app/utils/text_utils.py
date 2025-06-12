import re

from bs4 import BeautifulSoup


def slugify(text: str) -> str:
    """
    URL이나 파일명으로 사용할 수 있게 텍스트를 변환합니다.

    Args:
        text: 변환할 텍스트

    Returns:
        str: 변환된 텍스트
    """
    # 한글 특수 처리 (한글은 그대로 유지)
    text = re.sub(r'[^\w가-힣\s-]', '', text.lower())
    # 공백을 하이픈으로 변경
    text = re.sub(r'[\s]+', '-', text.strip())
    # 중복된 하이픈 제거
    text = re.sub(r'-+', '-', text)
    # 너무 긴 파일명 방지
    return text[:50] if len(text) > 50 else text

def clean_html_content(html_content: str) -> str:
    """
    HTML 콘텐츠에서 텍스트 추출 및 정리

    Args:
        html_content: HTML 형식 콘텐츠

    Returns:
        str: 정리된 텍스트
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text and clean up
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text
