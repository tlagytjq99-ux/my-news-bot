import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import os

def crawl_with_browser():
    url = "https://www.digital.go.jp/press?category=1"
    file_name = 'Japan_Digital_Policy_2025.csv'
    
    print("🚀 [브라우저 가동] 실제 화면을 렌더링하여 데이터를 추출합니다...")

    with sync_playwright() as p:
        # 브라우저 실행 (헤드리스 모드)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 페이지 접속 및 대기
            page.goto(url, wait_until="networkidle", timeout=60000)
            # 자바스크립트가 데이터를 불러올 시간을 줍니다.
            page.wait_for_timeout(5000) 
            
            # 렌더링된 HTML 가져오기
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # /press/ 링크 추출
            links = soup.find_all('a', href=True)
            policy_data = []

            for a in links:
                href = a['href']
                if '/press/' in href:
                    title = a.get_text(strip=True)
                    if len(title) < 10: continue
                    
                    policy_data.append({
                        "date": "2025/2026",
                        "title": title,
                        "link": "https://www.digital.go.jp" + href if href.startswith('/') else href
                    })

            if policy_data:
                unique_data = list({v['link']: v for v in policy_data}.values())
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                    writer.writeheader()
                    writer.writerows(unique_data)
                print(f"✅ [대성공] 브라우저 우회로 {len(unique_data)}건의 정책을 찾아냈습니다!")
            else:
                print("❌ 브라우저에서도 데이터를 찾지 못했습니다. 선택자 점검이 필요합니다.")
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    f.write("date,title,link\n")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")
        finally:
            browser.close()

if __name__ == "__main__":
    crawl_with_browser()
