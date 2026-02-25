import asyncio
from playwright.async_api import async_playwright
import csv

async def crawl_gartner_archive_ultimate():
    # 2025년과 2024년 두 페이지만 집중 공략
    target_years = ["2025", "2024"]
    file_name = 'Gartner_Insight_Archive.csv'
    all_data = []

    async with async_playwright() as p:
        # 1. 브라우저 실행 (가트너가 좋아하는 최신 크롬 버전으로 위장)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        print("🚀 Gartner 보안 우회 모드 가동...")

        for year in target_years:
            url = f"https://www.gartner.com/en/newsroom/archive/{year}"
            print(f"📡 {year}년 아카이브 접근 시도: {url}")
            
            try:
                # 2. 페이지 접속 (안정성을 위해 5초 대기)
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(5) 

                # 3. 화면을 아래로 천천히 스크롤 (데이터 로딩 유도)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                await asyncio.sleep(2)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

                # 4. 데이터 추출 로직 (클래스명을 더 포괄적으로 변경)
                items = await page.evaluate("""
                    () => {
                        const results = [];
                        // 가트너 뉴스 카드와 링크를 찾는 더 정교한 셀렉터
                        const links = document.querySelectorAll('a[href*="/en/newsroom/press-releases/"]');
                        
                        links.forEach(link => {
                            const title = link.innerText.trim();
                            const href = link.href;
                            // 제목이 너무 짧은 건 제외
                            if (title.length > 10) {
                                results.push({
                                    date: "Archive", // 상세 페이지 들어가야 날짜가 보이지만 일단 보류
                                    title: title.replace(/\\n/g, ' '),
                                    link: href
                                });
                            }
                        });
                        return results;
                    }
                """)
                
                if items:
                    all_data.extend(items)
                    print(f"✅ {year}년 데이터 {len(items)}건 확보!")
                else:
                    print(f"⚠️ {year}년 데이터가 보이지 않습니다. 구조가 변경되었을 수 있습니다.")

            except Exception as e:
                print(f"❌ {year}년 수집 중 오류: {str(e)[:100]}")
                continue

        await browser.close()

    # 5. 수집된 데이터가 1건이라도 있으면 강제로 파일 생성
    if all_data:
        # 중복 제거
        unique_data = {item['link']: item for item in all_data}.values()
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(unique_data)
        print(f"\n✨ [최종 성공] {len(unique_data)}건의 파일을 생성했습니다.")
    else:
        # 파일이 안 만들어져서 에러 나는 걸 방지하기 위해 빈 파일이라도 생성
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            f.write("date,title,link\\n")
        print("\n⚠️ 수집된 데이터가 없어 빈 파일을 생성했습니다.")

if __name__ == "__main__":
    asyncio.run(crawl_gartner_archive_ultimate())
