import asyncio
from playwright.sync_api import sync_playwright
import csv
import os

def crawl_with_brute_force_browser():
    url = "https://www.digital.go.jp/press?category=1"
    file_name = 'Japan_Digital_Policy_2025.csv'
    
    print("🚀 [최후의 수단] 스크롤링 및 지연 로딩 대응 모드 가동...")

    with sync_playwright() as p:
        # 실제 크롬 브라우저와 똑같이 보이도록 세팅
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # 1. 페이지 접속
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 2. 강제 대기 및 스크롤 (데이터 로딩 유도)
            print("⏳ 데이터 로딩을 위해 7초간 대기하며 스크롤합니다...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(7000) 

            # 3. 페이지 내 모든 <a> 태그 정보를 가져옴
            links = page.query_selector_all('a')
            policy_data = []

            for a in links:
                try:
                    href = a.get_attribute('href') or ""
                    title = a.inner_text() or ""
                    
                    # 정책 기사 패턴 (/press/숫자 혹은 ID)
                    if '/press/' in href and len(title.strip()) > 10:
                        full_url = href if href.startswith('http') else "https://www.digital.go.jp" + href
                        policy_data.append({
                            "date": "2025-2026",
                            "title": title.strip().replace('\n', ' '),
                            "link": full_url
                        })
                except:
                    continue

            # 4. 데이터 저장
            if policy_data:
                # 중복 제거
                unique_data = list({v['link']: v for v in policy_data}.values())
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(unique_data)
                print(f"✅ [감격] 드디어 {len(unique_data)}건의 데이터를 확보했습니다!")
            else:
                # 끝까지 안 나올 경우 빈 파일이라도 생성
                print("⚠️ 모든 수단을 동원했으나 기사를 찾지 못했습니다. 사이트 점검이 필요합니다.")
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    f.write("date,title,link\n")

        except Exception as e:
            print(f"❌ 실행 중 오류: {e}")
            with open(file_name, 'w', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")
        finally:
            browser.close()

if __name__ == "__main__":
    crawl_with_brute_force_browser()
