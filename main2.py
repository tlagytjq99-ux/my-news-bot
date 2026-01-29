import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config, site_name):
    """상세 페이지 날짜 추출 (AI타임스 로딩 대기 강화)"""
    try:
        # AI타임스일 경우 더 오래 기다리도록 설정 변경
        current_config = config
        if site_name == "AI타임스":
            current_config.wait_for = ".date" # 날짜 클래스가 나타날 때까지 대기
            current_config.delay_before_return_html = 8.0 # 충분한 로딩 시간

        result = await crawler.arun(url=url, config=current_config)
        if not (result.success and result.markdown): return "날짜확인필요"
        
        content = result.markdown[:3000] # 상단 데이터 집중 분석

        # 1. AI타임스 정밀 분석 (2026.01.29 10:30 형태 대응)
        if site_name == "AI타임스":
            date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', content)
            if date_match: return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"

        # 2. 백악관/해외 사이트 (January 29, 2026 형태)
        eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
        if eng_match:
            dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")

    except: pass
    return datetime.now().strftime("%Y-%m-%d") # 실패 시 오늘 날짜로 방어

async def main():
    # 🎯 백악관은 'AI' 검색 결과 주소로 직접 접속하도록 수정
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "백악관(AI검색)": "https://www.whitehouse.gov/?s=AI&post_type=briefing-room" 
    }

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", delay_before_return_html=5.0)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 수집 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 마크다운 핀셋 추출
                links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    if any(x in link.lower() for x in ['facebook', 'twitter', '.jpg']): continue

                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    print(f"   🔎 상세 분석: {title_clean[:20]}...")
                    exact_date = await get_exact_date(crawler, full_link, run_config, site_name)

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 5: break # 사이트당 5개씩

    # 저장 (CSV)
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    
    print(f"\n🎉 완료! '{file_name}' 파일을 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())
