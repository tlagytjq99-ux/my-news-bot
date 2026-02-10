import asyncio
from playwright.async_api import async_playwright
import csv

async def crawl_digital_2025_playwright_fixed():
    start_page = 21
    end_page = 188
    file_name = 'Japan_Digital_2025_Full_Archive.csv'
    all_data = []
    seen_links = set()

    async with async_playwright() as p:
        # 브라우저 실행
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page_obj = await context.new_page()

        print(f"🚀 [브라우저 모드] {start_page} ~ {end_page} 페이지 정밀 스캔 시작...")

        for p_num in range(start_page, end_page + 1):
            url = f"https://www.digital.go.jp/news?page={p_num}"
            
            try:
                # 페이지 접속 및 네트워크 안정화 대기
                await page_obj.goto(url, wait_until="domcontentloaded", timeout=60000)
                # 데이터 로딩을 위해 아주 잠깐 대기
                await asyncio.sleep(1.5) 

                # [수정 완료] results.append -> results.push 로 변경
                links = await page_obj.evaluate("""
                    () => {
                        const results = [];
                        const anchors = document.querySelectorAll('a[href*="/news/"], a[href*="/press/"], a[href*="/policies/"]');
                        anchors.forEach(a => {
                            const text = a.innerText.trim();
                            if (text.length > 15) {
                                results.push({
                                    title: text.replace(/\\n/g, ' '),
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
                
                print(f"📡 {p_num}/{end_page} 완료 | 현재 누적: {len(all_data)}건", end='\r')

            except Exception as e:
                print(f"\n❌ {p_num}페이지 로드 실패: {str(e)[:100]}")
                continue

        await browser.close()

    # CSV 저장 (UTF-8-SIG로 엑셀 한글/일어 깨짐 방지)
    if all_data:
        # 날짜순 정렬 시도 (타이틀 앞에 날짜가 오는 경우가 많으므로)
        all_data.sort(key=lambda x: x['title'], reverse=True)
        
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["title", "link"])
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\n\n✅ [임무 완수] 총 {len(all_data)}건의 데이터를 확보했습니다!")
    else:
        print("\n⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    asyncio.run(crawl_digital_2025_playwright_fixed())
