import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """상세 페이지에서 날짜를 파내고 표준 형식(YYYY-MM-DD)으로 변환합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown
        header = content[:2000] # 상단 2000자 집중 탐색

        # 1. 한국형 날짜 (AI타임스 등)
        match = re.search(r'(\d{4}\.\d{2}\.\d{2})', header)
        if match: return match.group(1).replace('.', '-')

        # 2. 영문형 날짜 (백악관, 벤처비트 등: January 28, 2026)
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', header)
        if eng_match:
            try:
                dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
                return dt.strftime("%Y-%m-%d")
            except: pass
            
        # 3. 기타 숫자 형식 (2026-01-28)
        date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', header)
        if date_match: return date_match.group(1).replace('/', '-')
            
    except: pass
    return "날짜확인필요"

async def main():
    # 🔗 백악관 뉴스룸 추가 (AI 관련 검색 필터링을 위해 기본 주소 사용)
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(AI)": "https://www.whitehouse.gov/briefing-room/statements-releases/"
    }

    # ✅ 백악관 등에서 AI 관련 기사만 골라내기 위한 키워드
    ai_keywords = ['ai', 'intelligence', 'tech', 'digital', 'algorithm', 'data', 'computing', '인공지능', '데이터']
    allowed_years = ['2025', '2026']
    
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", delay_before_return_html=5.0)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 데이터 수집 및 AI 필터링 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 🔍 [백악관 전용] 제목에 AI 키워드가 없으면 건너뜀
                    if site_name == "백악관(AI)":
                        if not any(kw in title_clean.lower() for kw in ai_keywords):
                            continue

                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png']): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    print(f"   🔎 날짜 매칭: {title_clean[:15]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)
                    
                    if not any(year in exact_date for year in allowed_years):
                        if exact_date != "날짜확인필요": continue

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 8: break

    # ✅ 정렬: 출처별 -> 발행일순(최신순)
    final_data.sort(key=lambda x: (x['출처'], x['발행일']), reverse=False)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\n🎉 성공! 백악관을 포함한 리포트 '{file_name}'가 생성되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
