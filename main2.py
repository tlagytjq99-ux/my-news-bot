import asyncio
import csv
import json
import re
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 🔗 수집하고 싶은 AI 뉴스 사이트 링크들입니다. 
    # 앞으로 다른 AI 사이트를 발견하시면 이 리스트에 주소만 추가하시면 됩니다!
    urls = [
        "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1", # AI타임스
        "https://venturebeat.com/category/ai/", # 벤처비트 (해외)
        "https://www.artificialintelligence-news.com/", # AI 뉴스 (해외)
        "https://www.theverge.com/ai-artificial-intelligence" # 더 버지 AI 섹션
    ]

    # [범용 규칙] AI 뉴스 사이트들의 공통 구조를 타겟팅합니다.
    schema = {
        "name": "AI_News_Scanner",
        "baseSelector": "article, .item, .list-block, .post-block, li", # 뉴스 한 줄의 단위
        "fields": [
            {"name": "title", "selector": "h2, h3, h4, .tit, .title", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
            {"name": "date", "selector": "time, .date, .dt, span.time", "type": "text"}
        ]
    }

    final_results = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            print(f"📡 {url} 에서 AI 뉴스 찾는 중...")
            
            result = await crawler.arun(
                url=url,
                extraction_strategy=JsonCssExtractionStrategy(schema),
                bypass_cache=True
            )

            if result.success and result.extracted_content:
                items = json.loads(result.extracted_content)
                count = 0
                for item in items:
                    title = item.get("title", "").strip()
                    link = item.get("link", "")
                    
                    # 1. 쓸모없는 짧은 텍스트(메뉴 등) 제외
                    if len(title) < 12 or not link or "javascript" in link:
                        continue
                    
                    # 2. 날짜 정리 (텍스트에서 날짜 형태만 추출)
                    raw_date = item.get("date", "")
                    date_match = re.search(r'(\d{4})[-./](\d{1,2})[-./](\d{1,2})', raw_date)
                    if date_match:
                        clean_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                    else:
                        clean_date = today_str # 날짜 못 찾으면 오늘 날짜로 표시

                    # 3. 링크 주소 보정
                    full_link = link if link.startswith('http') else f"{url.split('/')[0]}//{url.split('/')[2]}{link}"

                    final_results.append({
                        "수집일": today_str,
                        "발행일": clean_date,
                        "제목": title,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 5: break # 사이트당 5개만!
                
                print(f"✅ {url}: {count}개 수집 완료")

    # 엑셀(CSV) 저장
    with open('ai_trend_report.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_results)
    
    print(f"\n✨ 모든 수집 완료! 총 {len(final_results)}개의 뉴스가 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
