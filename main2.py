import asyncio
import csv
import os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    urls = [
        "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "https://venturebeat.com/category/ai/",
        "https://www.artificialintelligence-news.com/"
    ]

    final_data = []
    today = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            try:
                print(f"📡 {url} 시도 중...")
                # 추출 전략 없이 그냥 마크다운으로 통째로 가져옵니다.
                result = await crawler.arun(url=url, bypass_cache=True)

                if result.success and result.markdown:
                    # 마크다운 안에서 링크 형태 [제목](주소) 만 골라냅니다.
                    import re
                    links = re.findall(r'\[([^\]]{10,})\]\(([^\)]+)\)', result.markdown)
                    
                    added = 0
                    for title, link in links:
                        if "http" not in link and not link.startswith("/"): continue
                        if any(x in title.lower() for x in ["terms", "privacy", "about", "contact"]): continue
                        
                        final_data.append({
                            "수집일": today,
                            "발행일": today,
                            "제목": title.strip(),
                            "링크": link if link.startswith("http") else url + link
                        })
                        added += 1
                        if added >= 5: break
                    print(f"✅ {url}: {added}개 발견")
            except Exception as e:
                print(f"❌ {url} 에러: {e}")

    # [핵심] 데이터가 없어도 파일을 만듭니다.
    if not final_data:
        final_data.append({"수집일": today, "발행일": "-", "제목": "수집된 데이터가 없습니다. 사이트 차단을 확인하세요.", "링크": "-"})

    with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"💾 파일 저장 완료: {os.path.abspath('ai_trend_report.csv')}")

if __name__ == "__main__":
    asyncio.run(main())
