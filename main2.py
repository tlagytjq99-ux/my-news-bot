import asyncio
import csv
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # 1. 실행 설정 조정 (기다리는 시간을 조금 줄이고 에러 시 넘어가게 함)
    run_config = CrawlerRunConfig(
        wait_for="article, h2, h3", 
        wait_for_timeout=20000, # 20초만 기다리고 안 나오면 패스
        cache_mode=CacheMode.BYPASS,
        delay_before_return_html=1.0 
    )

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
            try: # 💡 안전장치 추가: 에러 나도 멈추지 마!
                print(f"📡 {url} 수집 시작...")
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
                        
                        from urllib.parse import urljoin
                        full_link = urljoin(url, link)

                        final_data.append({
                            "수집일": today,
                            "발행일": today,
                            "제목": title,
                            "링크": full_link
                        })
                        count += 1
                        if count >= 5: break
                    print(f"✅ {url}: {count}개 완료")
                else:
                    print(f"⚠️ {url}: 추출 결과 없음")

            except Exception as e:
                print(f"❌ {url} 작업 중 에러 발생 (건너뜁니다): {e}")
                continue

    # 2. 에러가 났어도 지금까지 수집된 건 무조건 저장
    if final_data:
        with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
            writer.writeheader()
            writer.writerows(final_data)
        print(f"🎉 성공! 총 {len(final_data)}개의 뉴스를 저장했습니다.")
    else:
        print("😭 저장할 데이터가 하나도 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())
