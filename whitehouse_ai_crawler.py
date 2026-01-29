import asyncio
import csv
import re
import os
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # 🎯 검색어: Artificial Intelligence
    search_url = "https://www.whitehouse.gov/?s=Artificial+Intelligence"
    file_name = 'whitehouse_ai_report.csv'
    
    print(f"📡 백악관 뉴스룸 정밀 스캔 시작 (범용 모드)...")

    existing_titles = set()
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader: existing_titles.add(row['제목'])

    # 💡 브라우저 설정을 더 '사람'처럼 보이게 강화합니다.
    browser_config = BrowserConfig(
        browser_type="chromium", 
        headless=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
    
    # 💡 특정 요소를 기다리지 않고, 페이지 로딩 후 10초만 딱 기다립니다.
    run_config = CrawlerRunConfig(
        delay_before_return_html=10.0, 
        cache_mode="bypass"
    )

    new_data = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=run_config)
        
        if result.success and result.markdown:
            print("✅ 페이지 로드 성공! 데이터를 분석합니다.")
            
            # 💡 [핵심] 백악관 뉴스룸의 링크 패턴을 더 넓게 잡습니다.
            # 1단계: 마크다운에서 모든 링크와 제목 추출
            all_links = re.findall(r'\[([^\]]{10,})\]\((https://www\.whitehouse\.gov/[^\)]+)\)', result.markdown)
            
            # AI 키워드 (테스트를 위해 범위를 넓힙니다)
            ai_keywords = ['AI', 'ARTIFICIAL INTELLIGENCE', 'TECH', 'CYBER', 'DIGITAL', 'DATA']
            
            count = 0
            for title, link in all_links:
                if count >= 5: break
                
                title_clean = title.strip().replace('\n', ' ')
                
                # 🎯 필터: 제목에 AI 키워드가 있고, 주소에 briefing-room이 포함된 진짜 뉴스만!
                if any(kw in title_clean.upper() for kw in ai_keywords):
                    if 'briefing-room' in link and title_clean not in existing_titles:
                        print(f"   🆕 발견: {title_clean[:40]}...")
                        
                        new_data.append({
                            "기관": "백악관(White House)",
                            "발행일": datetime.now().strftime("%Y-%m-%d"), # 상세페이지 에러 방지를 위해 일단 오늘날짜
                            "제목": title_clean,
                            "링크": link,
                            "수집일": datetime.now().strftime("%Y-%m-%d")
                        })
                        count += 1

    # 💾 결과 저장 (누적 모드)
    if new_data:
        file_exists = os.path.exists(file_name)
        with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
            if not file_exists: writer.writeheader()
            writer.writerows(new_data)
        print(f"✅ 성공! {len(new_data)}건의 뉴스가 추가되었습니다.")
    else:
        print("💡 새로운 소식이 없거나 필터링되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
