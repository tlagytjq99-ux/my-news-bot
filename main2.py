import asyncio
import csv
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 1. 브라우저 설정 (에러 원인인 extra_http_headers 제거)
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # 2. 실행 설정
    run_config = CrawlerRunConfig(
        wait_for="article, h2, h3, .list-block", 
        cache_mode=CacheMode.BYPASS,
        delay_before_return_html=2.0 
    )

    # 3. 범용적인 추출 규칙
    schema = {
        "name": "AI_News_Extractor",
        "baseSelector": "article, .item, tr, li, .list-block", 
        "fields": [
            {"name": "title", "selector": "h2, h3, a.title, .tit", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
            {"name": "date", "selector": "time, .date, .dt, span", "type": "text"}
        ]
    }
    extraction_strategy = JsonCssExtractionStrategy(schema)

    urls = [
        "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "https://venturebeat.com/category/ai/",
        "https://www.artificialintelligence-news.com/"
    ]

    final_data = []
    today = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            print(f"📡 {url} 수집 시작 (Playwright 가동)...")
            
            result = await crawler.arun(
                url=url,
                config=run_config,
                extraction_strategy=extraction_strategy
            )

            if result.success and result.extracted_content:
                items = json.loads(result.extracted_content)
                count = 0
                for item in items:
                    title = item.get("title", "").strip()
                    link = item.get("link", "")
                    
                    if len(title) < 10 or not link: continue
                    
                    # 링크 주소 보정
                    if not link.startswith('http'):
                        from urllib.parse import urljoin
                        full_link = urljoin(url, link)
                    else:
                        full_link = link

                    final_data.append({
                        "수집일": today,
                        "발행일": today,
                        "제목": title,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 5: break
                print(f"✅ {url}: {count}개 수집 완료")

    # 결과물 저장
    with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)

if __name__ == "__main__":
    asyncio.run(main())
