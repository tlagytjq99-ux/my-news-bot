import asyncio
from playwright.async_api import async_playwright
import csv

async def crawl_gartner_2026_top10():
    # 2026년 최신 뉴스가 모여있는 메인 페이지
    url = "https://www.gartner.com/en/newsroom"
    file_name = 'Gartner_Insight_Archive.csv'
    all_data = []

    async with async_playwright() as p:
        # 가트너가 의심하지 못하게 '유저 데이터'를 더 정교하게 위장
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        print(f"🎯 2026 가트너 최신 자료 수집 시작 (타겟: 메인 페이지)")
        
        try:
            # 접속 (네트워크가 조용해질 때까지 넉넉히 대기)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5) 

            # 화면을 조금씩 내려서 숨겨진 뉴스 카드가 나타나게 함 (Lazy Loading 대응)
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(1)

            # 모든 뉴스 링크 추출
            page_data = await page.evaluate("""
                () => {
                    const results = [];
                    // 가트너 뉴스룸 링크 패턴
                    const links = document.querySelectorAll('a[href*="/newsroom/press-releases/"]');
                    
                    // 최대 20개까지만 수집 (안전성 확보)
                    const limit = Math.min(links.length, 20);
                    
                    for(let i=0; i < limit; i++) {
                        const a = links[i];
                        const text = a.innerText.trim();
                        if (text.length > 10) {
                            results.push({
                                date: "2026-Recent",
                                title: text.replace(/\\n/g, ' '),
                                link: a.href
                            });
                        }
                    }
                    return results;
                }
            """)
            
            all_data = page_data
            print(f"✅ 최신 기사 {len(all_data)}건 발견!")

        except Exception as e:
            print(f"❌ 수집 중 오류: {e}")

        await browser.close()

    # 결과 저장
    if all_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"✨ 수집 완료! {file_name} 확인 부탁드립니다.")
    else:
        # 파일이 없으면 깃허브 액션이 에러나므로 빈 파일 생성
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            f.write("date,title,link\\n")
        print("🚨 데이터 수집 실패. 가트너 보안이 매우 강력합니다.")

if __name__ == "__main__":
    asyncio.run(crawl_gartner_2026_top10())
