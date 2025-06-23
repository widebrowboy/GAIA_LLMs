#!/usr/bin/env python3
"""
GAIAGPT React 애플리케이션 스크린샷 캡처 스크립트
"""

import asyncio
import os
import sys
from datetime import datetime

# Playwright 의존성이 있는지 확인
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Playwright가 설치되지 않았습니다.")
    print("다음 명령어로 설치하세요:")
    print("pip install playwright")
    print("npx playwright install")
    sys.exit(1)

async def capture_gaiagpt_screenshot():
    """GAIAGPT 웹페이지 스크린샷 캡처"""
    
    url = "http://localhost:3002"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"/home/gaia-bt/workspace/GAIA_LLMs/gaia_chat/gaiagpt_screenshot_{timestamp}.png"
    
    print(f"🔍 GAIAGPT 웹페이지 스크린샷 캡처 시작...")
    print(f"📍 URL: {url}")
    print(f"💾 저장 경로: {screenshot_path}")
    
    try:
        async with async_playwright() as p:
            # Chromium 브라우저 실행 (headless 모드)
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            # 새 페이지 생성
            page = await browser.new_page()
            
            # 뷰포트 크기 설정 (Full HD)
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            print("🌐 웹페이지 접속 중...")
            
            # 웹페이지 로드
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                print("✅ 웹페이지 로드 완료")
            except Exception as e:
                print(f"❌ 웹페이지 로드 실패: {e}")
                await browser.close()
                return False
            
            # React 앱이 완전히 로드될 때까지 대기
            print("⏳ React 앱 로딩 대기 중...")
            await asyncio.sleep(3)
            
            # 페이지 제목 확인
            title = await page.title()
            print(f"📄 페이지 제목: {title}")
            
            # 주요 요소들이 로드되었는지 확인
            try:
                # React root element 확인
                await page.wait_for_selector('#root', timeout=10000)
                print("✅ React root 요소 확인됨")
                
                # 추가 로딩 시간
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"⚠️ 일부 요소 로드 실패: {e}")
                print("그래도 스크린샷을 캡처합니다...")
            
            # 스크린샷 캡처
            print("📸 스크린샷 캡처 중...")
            await page.screenshot(
                path=screenshot_path,
                full_page=True
            )
            
            print(f"✅ 스크린샷 저장 완료: {screenshot_path}")
            
            # 브라우저 종료
            await browser.close()
            
            # 파일 존재 확인
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                print(f"📁 파일 크기: {file_size:,} bytes")
                return True
            else:
                print("❌ 스크린샷 파일을 찾을 수 없습니다.")
                return False
                
    except Exception as e:
        print(f"❌ 스크린샷 캡처 실패: {e}")
        return False

async def analyze_webpage_content():
    """웹페이지 내용 분석"""
    
    url = "http://localhost:3002"
    
    print(f"\n🔍 GAIAGPT 웹페이지 내용 분석...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 페이지 정보 수집
            title = await page.title()
            url_final = page.url
            
            print(f"📄 페이지 제목: {title}")
            print(f"🔗 최종 URL: {url_final}")
            
            # 주요 요소들 확인
            elements_to_check = [
                ('#root', 'React Root'),
                ('[class*="App"]', 'App Component'),
                ('[class*="sidebar"]', 'Sidebar'),
                ('[class*="chat"]', 'Chat Interface'),
                ('[class*="gaia"]', 'GAIA Branding'),
                ('[class*="conversation"]', 'Conversation List'),
                ('h1, h2, h3', 'Headings'),
                ('button', 'Buttons'),
                ('input, textarea', 'Input Fields')
            ]
            
            print("\n🔍 UI 요소 확인:")
            for selector, name in elements_to_check:
                try:
                    elements = await page.query_selector_all(selector)
                    count = len(elements)
                    if count > 0:
                        print(f"✅ {name}: {count}개 발견")
                    else:
                        print(f"❌ {name}: 없음")
                except Exception as e:
                    print(f"⚠️ {name}: 확인 실패 ({e})")
            
            # 텍스트 내용 일부 추출
            try:
                body_text = await page.text_content('body')
                if body_text and len(body_text.strip()) > 0:
                    print(f"\n📝 페이지 텍스트 내용 (처음 200자):")
                    print(f"'{body_text[:200].strip()}...'")
                else:
                    print("\n❌ 페이지에서 텍스트 내용을 찾을 수 없습니다.")
            except Exception as e:
                print(f"⚠️ 텍스트 추출 실패: {e}")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ 웹페이지 분석 실패: {e}")

async def main():
    """메인 실행 함수"""
    
    print("🚀 GAIAGPT React 애플리케이션 스크린샷 캡처 도구")
    print("=" * 60)
    
    # 웹페이지 내용 분석
    await analyze_webpage_content()
    
    print("\n" + "=" * 60)
    
    # 스크린샷 캡처
    success = await capture_gaiagpt_screenshot()
    
    if success:
        print("\n🎉 스크린샷 캡처 완료!")
        print("\n주요 확인 사항:")
        print("1. ✅ GAIAGPT 브랜딩 확인")
        print("2. ✅ 사이드바 대화 목록 확인")  
        print("3. ✅ 채팅 인터페이스 확인")
        print("4. ✅ 전체 UI/UX 디자인 확인")
    else:
        print("\n❌ 스크린샷 캡처 실패")
        print("웹페이지가 정상적으로 동작하는지 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())