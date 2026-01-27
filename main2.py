import asyncio
import csv
import json
from datetime import datetime
from dateutil import parser
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# 날짜 변환 함수
def format_date(date_str):
    if not date_str: return datetime.now().strftime("%Y-%m-%d")
    try:
        return parser.parse(date_str, fuzzy=True).strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

async def main():
    # 수집 대상 (구조가 명확한 곳 위주로 우선 세팅)
    sources = [
        {"name": "NIA", "url": "https://www.nia.or.kr/site/nia_kor/ex/bbs/List.do?cbIdx=82618", "selector": "tr"},
        {"name": "AITimes", "url": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1", "selector": ".list-block"},
        {"name": "VentureBeat", "url": "https://venturebeat.com/category/ai/", "selector": ".article-item"},
        {"name": "AINews", "url": "https://www.artificialintelligence-news.com/", "selector": ".type-post"}
    ]

    # 공통 추출 스키마
    schema = {
        "name": "News List",
        "baseSelector": "article, tr, .list-block, .article-item, .type-post",
        "fields": [
            {"name": "title", "selector": "a, .tit, h2, h3", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
            {"name": "date", "selector": ".date, time, .dt", "type": "text"}
        ]
    }
    strategy = JsonCssExtractionStrategy(schema)

    today = datetime.now().strftime("%Y-%m-%d")
    final_data = []

    async with AsyncWebCrawler() as crawler:
        for source in sources:
            print(f"📡 {source['name']} 수집 시도 중...")
            result = await crawler.arun(
                url=source['url'],
                extraction_strategy=strategy,
                bypass_cache=True,
                wait_for=source['selector'] # 페이지가 다 로딩될 때까지 기다림
            )

            if result.success and result.extracted_content:
                items = json.loads(result.extracted_content)
                count = 0
                for item in items:
                    title = item.get("title", "").strip()
                    link = item.get("link", "")
                    
                    # 제목이 너무 짧거나 링크가 없으면 무시
                    if len(title) < 10 or not link: continue
                    
                    # 링크 보정
                    if link.startswith('/'):
                        from urllib.parse import urljoin
                        link = urljoin(source['url'], link)

                    final_data.append({
                        "수집일": today,
                        "발행일": format_date(item.get("date", "")),
                        "제목": title,
                        "링크": link
                    })
                    count += 1
                    if count >= 5: break
                print(f"✅ {source['name']}: {count}개 수집 성공")
            else:
                print(f"❌ {source['name']}: 데이터 추출 실패")

    # 결과 저장
    with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
        else:
            # 데이터가 없을 경우 에러 확인용 샘플 데이터 한 줄 삽입
            writer.writerow({"수집일": today, "발행일": "-", "제목": "데이터 수집 실패 - 규칙 재점검 필요", "링크": "-"})

if __name__ == "__main__":
    asyncio.run(main())
