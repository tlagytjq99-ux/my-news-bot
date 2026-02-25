import asyncio
from playwright.async_api import async_playwright
import csv
import datetime

async def crawl_gartner_archive():
    # 수집 대상 연도 (최근 1년치 포함)
    target_years = ["2025", "2024"]
    file_name = 'Gartner_Insight_Archive.csv'
    all_data = []

    async with async_playwright() as p:
        # 가짜 브라우저 설정 (가트너 보안 통과용)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        for year in target_years:
            print(f"📅 Gartner {year}년도 뉴스룸 아카이브 접속 중...")
            url = f"https://www.gartner.com/en/newsroom/archive/{year}"
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(3) # 자바스크립트 실행 대기

                # 뉴스 항목 추출 (가트너 특유의 뉴스 카드 클래스 타겟팅)
                # 뉴스룸 구조에 맞춰 최적화된 JS 코드
                items = await page.evaluate("""
                    () => {
                        const results = [];
                        const cards = document.querySelectorAll('div.news-card-content');
                        cards.forEach(card => {
                            const titleTag = card.querySelector('h3') || card.querySelector('a');
                            const linkTag = card.querySelector('a');
                            const dateTag = card.querySelector('.news-card-date');
                            
                            if (titleTag && linkTag) {
                                results.push({
                                    date: dateTag ? dateTag.innerText.trim() : 'N/A',
                                    title: titleTag.innerText.trim(),
                                    link: linkTag.href
                                });
                            }
                        });
                        return results;
                    }
                """)
                
                all_data.extend(items)
                print(f"✅ {year}년 데이터 {len(items)}건 확보 완료")

            except Exception as e:
                print(f"❌ {year}년도 수집 실패: {e}")
                continue

        await browser.close()

    # CSV 저장
    if all_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n🚀 [최종 결과] 가트너 인사이트 총 {len(all_data)}건 수집 성공!")
    else:
        print("⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    asyncio.run(crawl_gartner_archive())
