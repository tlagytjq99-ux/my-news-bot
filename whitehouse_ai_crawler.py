import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_whitehouse_details(crawler, url, config):
    """상세 페이지에서 정확한 발행일을 추출합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        # 백악관 날짜 패턴 추출 (예: January 29, 2026)
        content = result.markdown[:2500]
        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
        if date_match:
            dt = datetime.strptime(date_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
    except: pass
    return datetime.now().strftime("%Y-%m-%d")

async def main():
    # 🎯 [핵심] 백악관 뉴스룸 내 AI 검색 결과 주소
    search_url = "https://www.whitehouse.gov/?s=Artificial+Intelligence&post_type=briefing-room"
    
    print(f"📡 백악관 뉴스룸에서 AI 관련 최신 소식을 찾는 중...")

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    # 정부 사이트 보안 및 로딩 속도를 고려해 10초 대기 설정
    run_config = CrawlerRunConfig(wait_for="body", delay_before_return_html=10.0)

    final_data = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=run_config)
        
        if result.success and result.markdown:
            # 1. 마크다운에서 기사 링크와 제목 추출
            # 백악관 검색 결과의 전형적인 링크 패턴을 타겟팅합니다.
            links = re.findall(r'\[([^\]]{20,})\]\(([^\)]+)\)', result.markdown)
            
            count = 0
            for title, link in links:
                if count >= 5: break  # 🎯 딱 최신 5개만 수집
                
                title_clean = title.strip()
                # 불필요한 메뉴 링크나 이미지 링크 제외
                if any(x in link.lower() for x in ['facebook', 'twitter', '.jpg', '.png']): continue
                
                full_link = urljoin(search_url, link)
                
                # 중복 체크
                if any(d['제목'] == title_clean for d in final_data): continue

                print(f"   🔎 ({count+1}/5) 상세 분석 중: {title_clean[:30]}...")
                exact_date = await get_whitehouse_details(crawler, full_link, run_config)

                final_data.append({
                    "기관": "백악관(White House)",
                    "발행일": exact_date,
                    "제목": title_clean,
                    "링크": full_link,
                    "수집일": datetime.now().strftime("%Y-%m-%d")
                })
                count += 1
                await asyncio.sleep(2) # 서버 부하 방지용 매너 모드

    # 💾 결과 저장 (CSV)
    if final_data:
        file_name = 'whitehouse_ai_search_results.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "링크", "수집일"])
            writer.writeheader()
            writer.writerows(final_data)
        print(f"\n✅ 성공! 백악관 최신 AI 뉴스 5개가 '{file_name}'에 저장되었습니다.")
    else:
        print("\n❌ 검색 결과에서 적절한 기사를 찾지 못했습니다.")

if __name__ == "__main__":
    asyncio.run(main())
