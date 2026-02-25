import asyncio
from playwright.async_api import async_playwright
import csv

async def crawl_gartner_via_google():
    # 가트너 사이트 내의 2026년 뉴스룸 기사만 구글에서 검색
    search_url = "https://www.google.com/search?q=site:gartner.com/en/newsroom/press-releases+2026&tbm=nws"
    file_name = 'Gartner_Insight_Archive.csv'
    all_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 구글은 의심하지 않게 유저 에이전트 설정
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"📡 구글 뉴스를 통해 가트너 2026 자료 우회 수집 시작...")
        
        try:
            # 구글 뉴스 검색 결과 접속
            await page.goto(search_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            # 구글 뉴스 검색 결과에서 제목과 링크 추출
            items = await page.evaluate("""
                () => {
                    const results = [];
                    // 구글 뉴스 기사 블록들을 선택
                    const articles = document.querySelectorAll('div[data-ved]');
                    
                    articles.forEach(article => {
                        const titleTag = article.querySelector('div[role="heading"]');
                        const linkTag = article.querySelector('a');
                        
                        if (titleTag && linkTag && linkTag.href.includes('gartner.com')) {
                            results.push({
                                date: "2026-Fixed",
                                title: titleTag.innerText.replace(/\\n/g, ' '),
                                link: linkTag.href
                            });
                        }
                    });
                    return results;
                }
            """)
            
            # 상위 10개만 슬라이싱
            all_data = items[:10]
            print(f"✅ 구글 우회로 가트너 자료 {len(all_data)}건 발견!")

        except Exception as e:
            print(f"❌ 구글 우회 시도 실패: {e}")

        await browser.close()

    if all_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"✨ [우회 성공] {file_name} 저장 완료.")
    else:
        # 파일 에러 방지용 더미 데이터
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerow({"date": "2026-N/A", "title": "Manual Check Required", "link": "https://www.gartner.com/en/newsroom"})
        print("🚨 구글 뉴스에서도 결과가 나오지 않았습니다.")

if __name__ == "__main__":
    asyncio.run(crawl_gartner_via_google())
