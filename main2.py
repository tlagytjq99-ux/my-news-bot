import asyncio
import csv
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 1. 브라우저 설정 (Playwright의 강력한 기능들을 여기서 세팅)
    browser_config = BrowserConfig(
        browser_type="chromium", # 크롬 엔진 사용
        headless=True,           # 화면 없이 실행 (속도 향상)
        # 중요: 진짜 사람처럼 보이게 만드는 '지문(Fingerprint)' 설정
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"}
    )

    # 2. 크롤링 실행 설정 (Playwright가 사이트 접속 시 행동할 지침)
    run_config = CrawlerRunConfig(
        # 데이터가 뜰 때까지 충분히 기다림 (Playwright의 대기 기능)
        wait_for="article, h2, h3, .list-block", 
        check_all_iframes=True,  # 숨겨진 프레임까지 확인
        cache_mode=CacheMode.BYPASS, # 매번 새로 고침해서 최신 데이터 수집
        # 페이지 로딩 후 2초간 더 대기 (자바스크립트 실행 완료 기다림)
        delay_before_return_html=2.0 
    )

    # 3. 범용적인 뉴스 추출 규칙
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

    # 수집 대상 AI 뉴스 사이트
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
                    
                    full_link = link if link.startswith('http') else f"{url.split('/')[0]}//{url.split('/')[2]}{link}"
                    
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
