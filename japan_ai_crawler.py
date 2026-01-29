import asyncio
import csv
import os
from datetime import datetime
from playwright.async_api import async_playwright

async def main():
    target_url = "https://www.cao.go.jp/houdou/houdou.html"
    file_name = 'japan_ai_report.csv'
    
    print(f"📡 [일본 내각부] Playwright 가상 브라우저 가동...")

    async with async_playwright() as p:
        # 브라우저 실행 (사람처럼 보이게 설정)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # 페이지 접속 및 로딩 대기
            await page.goto(target_url, wait_until="networkidle")
            await page.wait_for_timeout(3000) # 3초 추가 대기

            # 뉴스 링크들 추출
            # 일본 내각부 보도자료 리스트의 <a> 태그들을 타겟팅
            links = await page.query_selector_all("main a, #contents a, .main_list a")
            
            new_data = []
            existing_titles = set()
            if os.path.exists(file_name):
                with open(file_name, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader: existing_titles.add(row['제목'])

            count = 0
            for link_element in links:
                title = await link_element.inner_text()
                title = title.strip()
                url = await link_element.get_attribute("href")
                
                if not url: continue
                full_url = f"https://www.cao.go.jp{url}" if url.startswith("/") else url

                # 💡 필터링: 메뉴가 아닌 진짜 뉴스 제목처럼 긴 것만
                if len(title) > 20 and title not in existing_titles:
                    print(f"   🆕 발견: {title[:40]}...")
                    new_data.append({
                        "기관": "일본 내각부(CAO)",
                        "발행일": datetime.now().strftime("%Y-%m-%d"),
                        "제목": title,
                        "링크": full_url,
                        "수집일": datetime.now().strftime("%Y-%m-%d")
                    })
                    count += 1
                    if count >= 5: break

            # 저장 로직
            if new_data:
                file_exists = os.path.exists(file_name)
                with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
                    if not file_exists: writer.writeheader()
                    writer.writerows(new_data)
                print(f"✅ 성공! {len(new_data)}건의 데이터를 수집했습니다.")
            else:
                print("❌ 브라우저로 접속했으나 뉴스를 찾지 못했습니다.")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
