import asyncio
import csv
import re
import os
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_whitehouse_details(crawler, url, config):
    """상세 페이지에서 정확한 발행일 추출"""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        content = result.markdown[:2000]
        # 날짜 패턴: January 29, 2026
        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
        if date_match:
            dt = datetime.strptime(date_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
    except: pass
    return datetime.now().strftime("%Y-%m-%d")

async def main():
    # 🎯 검색어 'Artificial Intelligence'를 포함한 뉴스룸 주소
    search_url = "https://www.whitehouse.gov/?s=Artificial+Intelligence"
    file_name = 'whitehouse_ai_report.csv'
    
    print(f"📡 백악관 뉴스룸에서 'AI' 검색 결과를 정밀 스캔합니다...")

    existing_titles = set()
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader: existing_titles.add(row['제목'])

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    
    # 💡 [핵심 설정] 검색 결과 리스트(.search-results)가 다 뜰 때까지 기다립니다.
    run_config = CrawlerRunConfig(
        wait_for=".search-results__item", 
        delay_before_return_html=10.0, # 충분히 기다려야 검색 결과가 로딩됩니다.
        cache_mode="bypass"
    )

    new_data = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=run_config)
        
        if result.success and result.markdown:
            # 💡 [정밀 필터] 뉴스룸 검색 결과는 보통 특정 패턴의 링크를 가집니다.
            # 검색 결과 아이템 안에 있는 제목과 링크만 골라냅니다.
            # 마크다운에서 검색 아이템 패턴: [제목](https://www.whitehouse.gov/briefing-room/...)
            links = re.findall(r'\[([^\]]{20,})\]\((https://www\.whitehouse\.gov/briefing-room/[^\)]+)\)', result.markdown)
            
            # AI 관련 핵심 키워드 (제목에 포함 여부 확인)
            ai_keywords = ['AI', 'ARTIFICIAL INTELLIGENCE', 'TECH', 'DIGITAL', 'CYBER', 'QUANTUM']
            
            count = 0
            for title, link in links:
                if count >= 5: break
                
                title_clean = title.strip()
                
                # 제목에 AI 관련 단어가 있는지, 그리고 중복은 아닌지 확인
                if any(kw in title_clean.upper() for kw in ai_keywords) and title_clean not in existing_titles:
                    print(f"   🆕 발견: {title_clean[:40]}...")
                    exact_date = await get_whitehouse_details(crawler, link, run_config)

                    new_data.append({
                        "기관": "백악관(White House)",
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": link,
                        "수집일": datetime.now().strftime("%Y-%m-%d")
                    })
                    count += 1
                    await asyncio.sleep(2)

    # 💾 결과 저장
    if new_data:
        file_exists = os.path.exists(file_name)
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
            if not file_exists: writer.writeheader()
            writer.writerows(new_data)
        print(f"✅ 성공! {len(new_data)}건의 AI 뉴스가 추가되었습니다.")
    else:
        print("💡 새로운 AI 관련 뉴스가 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())
