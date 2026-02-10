import asyncio
from playwright.async_api import async_playwright
import csv

async def crawl_digital_2025_playwright():
    start_page = 21
    end_page = 188
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    all_data = []
    seen_links = set()

    async with async_playwright() as p:
        # 브라우저 실행 (headless=True는 화면 안 띄움)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page_obj = await context.new_page()

        print(f"🚀 [브라우저 모드] {start_page} ~ {end_page} 페이지 정밀 스캔 시작...")

        for p_num in range(start_page, end_page + 1):
            url = f"https://www.digital.go.jp/news?page={p_num}"
            
            try:
                # 페이지 접속 및 로딩 대기
                await page_obj.goto(url, wait_until="networkidle", timeout=60000)
                # 데이터가 로드될 때까지 1초 더 대기
                await asyncio.sleep(1) 

                # 페이지 내의 모든 뉴스 링크 추출
                # evaluate를 써서 브라우저 내부 자바스크립트로 직접 링크를 뽑습니다.
                links = await page_obj.evaluate("""
                    () => {
                        const results = [];
                        const anchors = document.querySelectorAll('a[href*="/news/"], a[href*="/press/"], a[href*="/policies/"]');
                        anchors.forEach(a => {
                            if (a.innerText.length > 15) {
                                results.append({
                                    title: a.innerText.replace(/\\n/g, ' ').trim(),
                                    href: a.href
                                });
                            }
                        });
                        return results;
                    }
                """)

                for link in links:
                    if link['href'] not in seen_links:
                        seen_links.add(link['href'])
                        all_data.append({
                            "title": link['title'],
                            "link": link['href']
                        })
                
                print(f"📡 {p_num}/{end_page} 완료 | 누적: {len(all_data)}건", end='\r')

            except Exception as e:
                print(f"\n❌ {p_num}페이지 로드 실패: {e}")
                continue

        await browser.close()

    # CSV 저장
    if all_data:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n\n✅ [임무 완수] 총 {len(all_data)}건의 데이터를 확보했습니다!")
    else:
        print("\n⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    asyncio.run(crawl_digital_2025_playwright())
