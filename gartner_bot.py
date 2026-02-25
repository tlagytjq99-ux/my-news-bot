import asyncio
from playwright.async_api import async_playwright
import csv

async def crawl_gartner_rss_safe():
    # 가트너가 공식적으로 제공하는 뉴스 RSS 피드 (보안 검사가 훨씬 약함)
    url = "https://www.gartner.com/it/content/xml/newsroom.xml"
    file_name = 'Gartner_Insight_Archive.csv'
    all_data = []

    async with async_playwright() as p:
        # 브라우저 대신 단순 리퀘스트 모드로 동작 시도
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"📡 가트너 RSS 전용 채널 접속 시도...")
        
        try:
            # RSS는 가볍기 때문에 타임아웃을 30초로 줄여도 충분합니다.
            response = await page.goto(url, wait_until="commit", timeout=30000)
            
            # XML 데이터 파싱 (제목과 링크 추출)
            content = await page.content()
            
            # 간단한 텍스트 파싱으로 2026년 최신 데이터 10개 추출
            import re
            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', content)
            links = re.findall(r'<link>(.*?)</link>', content)

            for i in range(min(len(titles), 15)):
                # RSS 최상단은 보통 뉴스룸 메인이므로 제외
                if "Newsroom" in titles[i] and i == 0: continue
                
                all_data.append({
                    "date": "2026-Latest",
                    "title": titles[i].strip(),
                    "link": links[i].strip()
                })
            
            print(f"✅ RSS를 통해 최신 자료 {len(all_data)}건 확보!")

        except Exception as e:
            print(f"❌ RSS 접속 실패: {e}")
            # 만약 RSS도 막혔다면, 최종 수단으로 '구글 뉴스' 검색 결과 우회 시도 코드로 자동 전환 가능

        await browser.close()

    if all_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"✨ [성공] {file_name} 저장 완료.")
    else:
        # 빈 파일이라도 생성하여 에러 방지
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            f.write("date,title,link\n")
        print("🚨 모든 우회로가 차단되었습니다.")

if __name__ == "__main__":
    asyncio.run(crawl_gartner_rss_safe())
