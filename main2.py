import asyncio
import csv
import re
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def get_exact_date(crawler, url, config):
    """기사 상세 페이지에서 실제 발행일을 정밀 추출합니다."""
    try:
        result = await crawler.arun(url=url, config=config)
        if result.success and result.markdown:
            content = result.markdown
            
            # 1. AI타임스 등 한국형 패턴
            date_match = re.search(r'(\d{4}[-./]\d{2}[-./]\d{2})', content)
            if date_match:
                return date_match.group(1).replace('.', '-').replace('/', '-')
            
            # 2. 영문형 패턴 (벤처비트/테크크런치/백악관)
            eng_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
            if eng_match:
                dt = datetime.strptime(eng_match.group(1), "%B %d, %Y")
                return dt.strftime("%Y-%m-%d")
    except: pass
    return "날짜확인필요"

async def main():
    target_sites = {
        "AI타임스": "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1",
        "벤처비트": "https://venturebeat.com/category/ai/",
        "테크크런치": "https://techcrunch.com/category/artificial-intelligence/",
        "백악관(AI)": "https://www.whitehouse.gov/briefing-room/statements-releases/"
    }

    ai_keywords = ['ai', 'intelligence', 'tech', 'digital', 'data', 'algorithm', 'cyber', '인공지능', '데이터', '디지털']
    
    # 📅 [연도 필터] 최신 트렌드를 위해 2025년 이후 기사만 허용
    allowed_years = ['2025', '2026']

    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    run_config = CrawlerRunConfig(wait_for="body", wait_for_timeout=20000)
    
    final_data = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for site_name, url in target_sites.items():
            print(f"📡 [{site_name}] 최신 뉴스 필터링 수집 중...")
            list_result = await crawler.arun(url=url, config=run_config)

            if list_result.success and list_result.markdown:
                # 벤처비트 등의 사이드바 노이즈를 줄이기 위해 목록 본문만 타겟팅
                links = re.findall(r'\[([^\]]{25,})\]\(([^\)]+)\)', list_result.markdown)
                
                count = 0
                for title, link in links:
                    title_clean = re.sub(r'[\[\]\r\n\t]', '', title).strip()
                    
                    # 🔍 키워드 및 노이즈 필터링
                    if site_name == "백악관(AI)" and not any(kw in title_clean.lower() for kw in ai_keywords): continue
                    if "![" in title or any(ext in link.lower() for ext in ['.jpg', '.png', '.jpeg']): continue
                    
                    full_link = urljoin(url, link)
                    if any(d['제목'] == title_clean for d in final_data): continue

                    # 📅 상세 페이지 날짜 추출
                    exact_date = await get_exact_date(crawler, full_link, run_config)
                    
                    # 🚫 [연도 필터 적용] 2025년이나 2026년이 아니면 과감히 버림
                    if not any(year in exact_date for year in allowed_years):
                        # URL에 날짜 정보가 있는 경우 한 번 더 확인
                        url_date_match = re.search(r'/(\d{4})/', full_link)
                        if url_date_match and url_date_match.group(1) not in allowed_years:
                            continue
                        elif exact_date != "날짜확인필요" and not any(year in exact_date for year in allowed_years):
                            continue

                    final_data.append({
                        "출처": site_name,
                        "수집일": today_str,
                        "발행일": exact_date,
                        "제목": title_clean,
                        "링크": full_link
                    })
                    count += 1
                    if count >= 8: break

    # CSV 저장 (내림차순 정렬: 최신순)
    final_data.sort(key=lambda x: x['발행일'], reverse=True)
    
    file_name = 'ai_trend_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["출처", "수집일", "발행일", "제목", "링크"])
        writer.writeheader()
        writer.writerows(final_data)
    print(f"🎉 2025-2026 최신 기사 전용 리포트 생성 완료!")

if __name__ == "__main__":
    asyncio.run(main())
