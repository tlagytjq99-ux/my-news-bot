import asyncio
import csv
import json
import re
from datetime import datetime
from dateutil import parser  # 다양한 날짜 형식을 자동으로 해석
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# 날짜 형식을 YYYY-MM-DD로 정규화하는 함수
def format_date(date_str):
    if not date_str or date_str == "N/A":
        return datetime.now().strftime("%Y-%m-%d")
    try:
        # 상대적 시간 표현 처리 (예: "5 hours ago", "어제" 등)
        if 'ago' in date_str or '전' in date_str:
            return datetime.now().strftime("%Y-%m-%d")
        
        # 일반적인 날짜 문자열 해석
        parsed_date = parser.parse(date_str, fuzzy=True)
        return parsed_date.strftime("%Y-%m-%d")
    except:
        # 해석 실패 시 숫자만 추출 시도 (예: 2024.05.20 -> 2024-05-20)
        nums = re.findall(r'\d+', date_str)
        if len(nums) >= 3:
            return f"{nums[0]}-{nums[1].zfill(2)}-{nums[2].zfill(2)}"
        return datetime.now().strftime("%Y-%m-%d")

async def main():
    urls = [
        "https://www.nia.or.kr/site/nia_kor/ex/bbs/List.do?cbIdx=82618", # NIA
        "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1", # AI타임스
        "https://venturebeat.com/category/ai/", # VentureBeat
        "https://www.artificialintelligence-news.com/" # AI News
    ]

    # 추출 규칙: 제목, 링크, 날짜 정보만 타겟팅
    schema = {
        "name": "AI News Extractor",
        "baseSelector": "article, .item, tr, .type-post", 
        "fields": [
            {"name": "title", "selector": "h2, h3, .tit, a.title", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
            {"name": "date", "selector": "time, .date, .dt, .date-time", "type": "text"}
        ]
    }
    strategy = JsonCssExtractionStrategy(schema)

    today = datetime.now().strftime("%Y-%m-%d")
    final_data = []

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(url=url, extraction_strategy=strategy, bypass_cache=True)

            if result.success and result.extracted_content:
                items = json.loads(result.extracted_content)
                
                # 각 사이트당 최신 5개만 추출
                count = 0
                for item in items:
                    title = item.get("title", "").strip()
                    link = item.get("link", "")
                    
                    # 제목이 너무 짧거나 링크가 없는 광고성 데이터 필터링
                    if len(title) < 5 or not link:
                        continue
                    
                    # 링크가 상대경로인 경우 절대경로로 보정
                    if link.startswith('/'):
                        from urllib.parse import urljoin
                        link = urljoin(url, link)

                    final_data.append({
                        "수집일": today,
                        "발행일": format_date(item.get("date", "")),
                        "제목": title,
                        "링크": link
                    })
                    
                    count += 1
                    if count >= 5: break
                
                print(f"✅ {url}: 5개 수집 성공")

    # CSV 저장 (엑셀에서 바로 열리도록 utf-8-sig 사용)
    with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)

if __name__ == "__main__":
    asyncio.run(main())
